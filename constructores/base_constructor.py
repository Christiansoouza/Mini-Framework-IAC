from abc import ABC, abstractmethod
import time
import boto3
from botocore.exceptions import ClientError


class BaseConstructor(ABC):
    """Classe base para construtores de recursos AWS via CloudFormation"""

    def __init__(
        self,name: str,
        template_body: str, parameters: dict | None = None,
        profile: str | None = None, region: str | None = None,
    ):
        
        self.name = name
        self.template_body = template_body
        self.parameters = parameters or {}

        # Cria a sessão
        self.session = boto3.Session(
            profile_name=profile,
            region_name=region,
        )
		
		# Cria o cliente de CloudFormation
        self.cf_client = self.session.client("cloudformation")


    # =========================
    # Helpers CloudFormation
    # =========================

    def __stack_exists(self) -> bool:
        try:
            resp = self.cf_client.describe_stacks(StackName=self.name)
            
			# Verifica se o stack está em processo de revisão (ex: falha de criação) e trata como inexistente
            status = resp["Stacks"][0]["StackStatus"]
            if status == "DELETE_COMPLETE":
                return False
            # Tratar stacks em REVIEW_IN_PROGRESS como inexistentes para permitir re-criação automática
            if status == "REVIEW_IN_PROGRESS":
                print("⚠️ Stack em REVIEW_IN_PROGRESS detectado. Excluindo automaticamente...")
                self.cf_client.delete_stack(StackName=self.name)
                return False
            
            return True
        except ClientError as e:
            if "does not exist" in str(e):
                return False
            raise

    def _get_outputs(self) -> dict:
        resp = self.cf_client.describe_stacks(StackName=self.name)
        outputs = resp["Stacks"][0].get("Outputs", [])

        return {
            item["OutputKey"]: item["OutputValue"]
            for item in outputs
        }

    def __wait_changeset(self, change_set_name: str):
        while True:
            resp = self.cf_client.describe_change_set(
                StackName=self.name,
                ChangeSetName=change_set_name
            )

            status = resp["Status"]
            reason = resp.get("StatusReason", "")

            if status == "CREATE_COMPLETE":
                return resp

            if status == "FAILED":
                if "didn't contain changes" in reason:
                    print("✔ Nenhuma mudança detectada")
                    return None
                raise RuntimeError(
                    f"ChangeSet {change_set_name} falhou: {reason}"
                )

            time.sleep(3)
            
    def __print_changeset(self, changeset, show_replacement: bool = True):
        for change in changeset["Changes"]:
            r = change["ResourceChange"]

            line = (
                f"- {r['Action']:7} | "
                f"{r['LogicalResourceId']} | "
                f"{r['ResourceType']}"
            )

            if show_replacement:
                line += f" | Replacement={r.get('Replacement', 'N/A')}"

            print(line)



    def plan(self):
        """Cria Change Set e exibe o plano de execução"""
        change_set_name = f"plan-{int(time.time())}"
        change_set_type = "UPDATE" if self.__stack_exists() else "CREATE"

        print(f"📦 Criando Change Set ({change_set_type})")

        self.cf_client.create_change_set(
            StackName=self.name,
            ChangeSetName=change_set_name,
            ChangeSetType=change_set_type,
            TemplateBody=self.template_body,
            Parameters=[
                {"ParameterKey": k, "ParameterValue": str(v)}
                for k, v in self.parameters.items()
            ],
            Capabilities=[
                "CAPABILITY_IAM",
                "CAPABILITY_NAMED_IAM"
            ],
        )

        changeset = self.__wait_changeset(change_set_name)
        if not changeset:
            return None, None

        print("\n📋 Plano de mudanças:\n")

        self.__print_changeset(changeset, show_replacement=True)

        return change_set_name, change_set_type
    
    def destroy_plan(self):
        """Lista os recursos que serão destruídos (não faz plano real)"""
        if not self.__stack_exists():
            print("ℹ️ Stack não existe, nada para destruir")
            return None

        print("\n📋 Recursos existentes no stack que serão removidos:\n")
        resources = self.cf_client.describe_stack_resources(StackName=self.name)["StackResources"]
        for r in resources:
            print(f"- {r['LogicalResourceId']} | {r['ResourceType']} | Status={r['ResourceStatus']}")
        return True

    def deploy(self):
        """Aplica o Change Set"""
        change_set_name, change_set_type = self.plan()

        if not change_set_name:
            print("🚫 Nada para aplicar")
            return

        print("\n🚀 Executando Change Set")

        self.cf_client.execute_change_set(
            StackName=self.name,
            ChangeSetName=change_set_name
        )

        waiter = self.cf_client.get_waiter(
            "stack_create_complete"
            if change_set_type == "CREATE"
            else "stack_update_complete"
        )

        waiter.wait(StackName=self.name)
        print("✅ Deploy concluído com sucesso")

        outputs = self._get_outputs()
        print("📦 Outputs gerados:", outputs)

        return outputs

    def destroy(self):
        plan = self.destroy_plan()

        if not plan:
            print("🚫 Nada para destruir")
            return
        input("Pressione Enter para confirmar a destruição ou CTRL+Z para cancelar...")
        print("\n🔥 Executando destruição")
        self.cf_client.delete_stack(StackName=self.name)
        waiter = self.cf_client.get_waiter("stack_delete_complete")
        waiter.wait(StackName=self.name)
        print("🗑 Stack removida com sucesso")
        

	# =========================
    # Métodos obrigatórios
    # =========================

    @abstractmethod
    def output(self):
        """Retorna informações relevantes do recurso criado"""
        pass

    @abstractmethod
    def export_outputs_json(self):
        """Exporta os outputs para um formato consumível por outros construtores"""
        pass


