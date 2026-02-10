from abc import ABC, abstractmethod
import time
import boto3
from botocore.exceptions import ClientError


class BaseConstructor(ABC):
    """
    Classe base para construtores de recursos AWS via CloudFormation.

    Responsabilidades:
    - Gerencia criação, atualização e destruição de stacks CloudFormation.
    - Fornece interface comum para construtores específicos (VPC, ECR, ECS, RDS, etc).
    - Permite planejamento (plan), deploy, verificação de status, exportação de outputs e destruição de stacks.

    Métodos principais:
    - plan(): Exibe o plano de recursos a serem criados/alterados (simulação).
    - deploy(): Cria e executa ChangeSet, aplicando o template.
    - destroy(): Remove o stack e todos os recursos provisionados.
    - destroy_plan(): Lista recursos que serão removidos.
    - output(): Retorna informações relevantes do recurso criado (deve ser implementado nas subclasses).
    - export_outputs_json(): Exporta outputs para JSON (deve ser implementado nas subclasses).

    Parâmetros aceitos no construtor:
    - name: Nome do stack CloudFormation.
    - template_body: Template YAML/JSON do recurso.
    - parameters: Dicionário de parâmetros do template.
    - profile: Nome do perfil AWS (para autenticação).
    - region: Região AWS.

    Helpers:
    - _stack_exists(): Verifica existência do stack e trata estados inconsistentes.
    - _get_outputs(): Retorna outputs do stack.
    - __wait_changeset(): Aguarda execução de ChangeSet.
    - __print_changeset(): Exibe plano de mudanças.

    Uso:
    Herde esta classe para criar construtores específicos de cada recurso, implementando os métodos abstratos.
    """
    def __init__(
        self, name: str,
        template_body: str, profile: str, 
        region: str, parameters: dict = {},
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
        """Verifica se a stack existe, 
        	tratando estados inconsistentes como inexistente para permitir re-criação automática.
        """
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
        """"Retorna os outputs do stack como um dicionário simples {OutputKey: OutputValue}"""
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

            print(f"⏳ Aguardando Change Set... Status: {status} | Reason: {reason}")
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
        """Printa o plano de mudanças de forma legível"""
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



    def plan(self,deploy: bool = False):
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

        if not deploy:
            self.cf_client.delete_change_set(StackName=self.name)

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
        """Aplica o Change Set criando ou atualizando o stack conforme necessário e aguarda a conclusão do deploy"""
        change_set_name, change_set_type = self.plan(deploy=True)

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


    
    def output(self):
        """Retorna os outputs do stack como um dicionário simples {OutputKey: OutputValue}"""
        try:
            resp = self.cf_client.describe_stacks(StackName=self.name)
            outputs = resp["Stacks"][0].get("Outputs", [])
            return {item["OutputKey"]: item["OutputValue"] for item in outputs}
        except Exception as e:
            print(f"Erro ao obter outputs do stack {self.name}: {e}")
            return {}

    def export_outputs_json(self):
        """Exporta os outputs para um arquivo JSON de forma cumulativa"""
        import os
        import json
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output.json")
        # Carrega o arquivo se existir
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
        else:
            data = {}

        data[self.name] = self.output()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Outputs salvos em {output_path}")

