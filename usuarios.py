"""
Módulo de Usuários (Equipe 1)
Responsável pelo CRUD de usuários: Cadastrar, editar, remover e listar usuários.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import sys
sys.path.insert(0, '/home/ubuntu/sgbu_python')

from utils.excecoes import (
    UsuarioNaoEncontradoException,
    ValidacaoException,
    UsuarioPossuiEmprestimosAtivosException
)


class TipoUsuario(Enum):
    """Enum para tipos de usuários."""
    ALUNO = "Aluno"
    FUNCIONARIO = "Funcionário"
    PROFESSOR = "Professor"


class StatusUsuario(Enum):
    """Enum para status de usuários."""
    ATIVO = "Ativo"
    BLOQUEADO = "Bloqueado"
    INATIVO = "Inativo"


@dataclass
class Usuario:
    """Classe que representa um usuário da biblioteca."""
    matricula: str
    nome: str
    tipo: TipoUsuario
    status: StatusUsuario = StatusUsuario.ATIVO
    email: Optional[str] = None
    telefone: Optional[str] = None
    emprestimos_ativos: int = field(default=0)

    def __post_init__(self):
        """Valida os dados do usuário após a inicialização."""
        self._validar()

    def _validar(self):
        """Valida os dados do usuário."""
        if not self.matricula or not isinstance(self.matricula, str):
            raise ValidacaoException("Matrícula é obrigatória e deve ser uma string.")
        
        if not self.nome or not isinstance(self.nome, str):
            raise ValidacaoException("Nome é obrigatório e deve ser uma string.")
        
        if len(self.nome) < 3:
            raise ValidacaoException("Nome deve ter pelo menos 3 caracteres.")
        
        if len(self.nome) > 100:
            raise ValidacaoException("Nome não pode ter mais de 100 caracteres.")
        
        if not isinstance(self.tipo, TipoUsuario):
            raise ValidacaoException(f"Tipo de usuário inválido. Deve ser um dos: {[t.value for t in TipoUsuario]}")

    def to_dict(self):
        """Serializa o usuário para um dicionário (contrato de serialização)."""
        return {
            "matricula": self.matricula,
            "nome": self.nome,
            "tipo": self.tipo.value,
            "status": self.status.value,
            "email": self.email,
            "telefone": self.telefone,
            "emprestimos_ativos": self.emprestimos_ativos
        }


class ModuloUsuarios:
    """
    Módulo responsável pelo gerenciamento de usuários.
    Implementa CRUD e operações de validação.
    """

    def __init__(self):
        """Inicializa o módulo com um dicionário vazio de usuários."""
        self._usuarios: dict[str, Usuario] = {}

    def cadastrar_usuario(self, matricula: str, nome: str, tipo: str, email: Optional[str] = None, telefone: Optional[str] = None) -> Usuario:
        """
        Cadastra um novo usuário.
        
        Args:
            matricula: Matrícula única do usuário.
            nome: Nome completo do usuário.
            tipo: Tipo de usuário (Aluno, Funcionário, Professor).
            email: Email do usuário (opcional).
            telefone: Telefone do usuário (opcional).
        
        Returns:
            Usuario: O usuário cadastrado.
        
        Raises:
            ValidacaoException: Se os dados são inválidos.
        """
        if matricula in self._usuarios:
            raise ValidacaoException(f"Usuário com matrícula '{matricula}' já existe.")
        
        # Converte string para enum
        try:
            tipo_enum = TipoUsuario[tipo.upper()] if isinstance(tipo, str) else tipo
        except (KeyError, AttributeError):
            raise ValidacaoException(f"Tipo de usuário inválido: {tipo}. Deve ser um dos: {[t.name for t in TipoUsuario]}")
        
        usuario = Usuario(
            matricula=matricula,
            nome=nome,
            tipo=tipo_enum,
            email=email,
            telefone=telefone
        )
        
        self._usuarios[matricula] = usuario
        return usuario

    def obter_usuario(self, matricula: str) -> Usuario:
        """
        Obtém um usuário pela matrícula.
        
        Args:
            matricula: Matrícula do usuário.
        
        Returns:
            Usuario: O usuário encontrado.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
        """
        if matricula not in self._usuarios:
            raise UsuarioNaoEncontradoException(f"Usuário com matrícula '{matricula}' não encontrado.")
        
        return self._usuarios[matricula]

    def listar_usuarios(self) -> List[Usuario]:
        """
        Lista todos os usuários cadastrados.
        
        Returns:
            List[Usuario]: Lista de usuários.
        """
        return list(self._usuarios.values())

    def editar_usuario(self, matricula: str, nome: Optional[str] = None, tipo: Optional[str] = None, 
                       email: Optional[str] = None, telefone: Optional[str] = None) -> Usuario:
        """
        Edita os dados de um usuário existente.
        
        Args:
            matricula: Matrícula do usuário.
            nome: Novo nome (opcional).
            tipo: Novo tipo (opcional).
            email: Novo email (opcional).
            telefone: Novo telefone (opcional).
        
        Returns:
            Usuario: O usuário editado.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
            ValidacaoException: Se os dados são inválidos.
        """
        usuario = self.obter_usuario(matricula)
        
        if nome is not None:
            if len(nome) < 3:
                raise ValidacaoException("Nome deve ter pelo menos 3 caracteres.")
            usuario.nome = nome
        
        if tipo is not None:
            try:
                tipo_enum = TipoUsuario[tipo.upper()] if isinstance(tipo, str) else tipo
                usuario.tipo = tipo_enum
            except (KeyError, AttributeError):
                raise ValidacaoException(f"Tipo de usuário inválido: {tipo}.")
        
        if email is not None:
            usuario.email = email
        
        if telefone is not None:
            usuario.telefone = telefone
        
        return usuario

    def remover_usuario(self, matricula: str) -> bool:
        """
        Remove um usuário.
        
        Args:
            matricula: Matrícula do usuário.
        
        Returns:
            bool: True se removido com sucesso.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
            UsuarioPossuiEmprestimosAtivosException: Se o usuário possui empréstimos ativos.
        """
        usuario = self.obter_usuario(matricula)
        
        if usuario.emprestimos_ativos > 0:
            raise UsuarioPossuiEmprestimosAtivosException(
                f"Usuário '{matricula}' possui {usuario.emprestimos_ativos} empréstimo(s) ativo(s) e não pode ser removido."
            )
        
        del self._usuarios[matricula]
        return True

    def bloquear_usuario(self, matricula: str) -> Usuario:
        """
        Bloqueia um usuário.
        
        Args:
            matricula: Matrícula do usuário.
        
        Returns:
            Usuario: O usuário bloqueado.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
        """
        usuario = self.obter_usuario(matricula)
        usuario.status = StatusUsuario.BLOQUEADO
        return usuario

    def desbloquear_usuario(self, matricula: str) -> Usuario:
        """
        Desbloqueia um usuário.
        
        Args:
            matricula: Matrícula do usuário.
        
        Returns:
            Usuario: O usuário desbloqueado.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
        """
        usuario = self.obter_usuario(matricula)
        usuario.status = StatusUsuario.ATIVO
        return usuario

    def incrementar_emprestimos(self, matricula: str):
        """Incrementa o contador de empréstimos ativos de um usuário."""
        usuario = self.obter_usuario(matricula)
        usuario.emprestimos_ativos += 1

    def decrementar_emprestimos(self, matricula: str):
        """Decrementa o contador de empréstimos ativos de um usuário."""
        usuario = self.obter_usuario(matricula)
        if usuario.emprestimos_ativos > 0:
            usuario.emprestimos_ativos -= 1