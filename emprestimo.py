"""
Módulo de Controle de Empréstimo e Devolução (Equipe 3)
Responsável pelo registro de empréstimos, devoluções e verificação de disponibilidade.
Integra-se com os módulos de Usuários e Catálogo.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import sys
sys.path.insert(0, '/home/ubuntu/sgbu_python')

from utils.excecoes import (
    UsuarioNaoEncontradoException,
    UsuarioBloqueadoException,
    LivroNaoEncontradoException,
    LivroIndisponvelException,
    EmprestimoJaExisteException,
    EmprestimoNaoEncontradoException,
    ValidacaoException
)
from modulos.usuarios import ModuloUsuarios, StatusUsuario
from modulos.catalogo import ModuloCatalogo


class StatusEmprestimo(Enum):
    """Enum para status de empréstimos."""
    ATIVO = "Ativo"
    DEVOLVIDO = "Devolvido"
    ATRASADO = "Atrasado"


@dataclass
class Emprestimo:
    """Classe que representa um empréstimo."""
    id_emprestimo: str
    matricula_usuario: str
    isbn_livro: str
    data_emprestimo: datetime
    data_devolucao_prevista: datetime
    data_devolucao_real: Optional[datetime] = None
    status: StatusEmprestimo = StatusEmprestimo.ATIVO

    def to_dict(self):
        """Serializa o empréstimo para um dicionário (contrato de serialização)."""
        return {
            "id_emprestimo": self.id_emprestimo,
            "matricula_usuario": self.matricula_usuario,
            "isbn_livro": self.isbn_livro,
            "data_emprestimo": self.data_emprestimo.isoformat(),
            "data_devolucao_prevista": self.data_devolucao_prevista.isoformat(),
            "data_devolucao_real": self.data_devolucao_real.isoformat() if self.data_devolucao_real else None,
            "status": self.status.value
        }


class ModuloEmprestimo:
    """
    Módulo responsável pelo gerenciamento de empréstimos e devoluções.
    Integra-se com os módulos de Usuários e Catálogo.
    """

    def __init__(self, modulo_usuarios: ModuloUsuarios, modulo_catalogo: ModuloCatalogo):
        """
        Inicializa o módulo de empréstimo.
        
        Args:
            modulo_usuarios: Referência ao módulo de usuários.
            modulo_catalogo: Referência ao módulo de catálogo.
        """
        self._emprestimos: dict[str, Emprestimo] = {}
        self._modulo_usuarios = modulo_usuarios
        self._modulo_catalogo = modulo_catalogo
        self._contador_emprestimos = 0

    def registrar_emprestimo(self, matricula_usuario: str, isbn_livro: str, dias_emprestimo: int = 7) -> Emprestimo:
        """
        Registra um novo empréstimo.
        
        Integração com Módulo de Usuários:
            - Verifica se o usuário existe.
            - Verifica se o usuário está bloqueado.
            - Incrementa o contador de empréstimos do usuário.
        
        Integração com Módulo de Catálogo:
            - Verifica se o livro existe.
            - Verifica se o livro está disponível (estoque > 0).
            - Decrementa o estoque do livro.
        
        Args:
            matricula_usuario: Matrícula do usuário.
            isbn_livro: ISBN do livro.
            dias_emprestimo: Número de dias para o empréstimo (padrão: 7).
        
        Returns:
            Emprestimo: O empréstimo registrado.
        
        Raises:
            UsuarioNaoEncontradoException: Se o usuário não existe.
            UsuarioBloqueadoException: Se o usuário está bloqueado.
            LivroNaoEncontradoException: Se o livro não existe.
            LivroIndisponvelException: Se o livro não está disponível.
            EmprestimoJaExisteException: Se o usuário já tem um empréstimo ativo do mesmo livro.
        """
        # Integração com Módulo de Usuários (IT-001, IT-002, IT-005)
        try:
            usuario = self._modulo_usuarios.obter_usuario(matricula_usuario)
        except UsuarioNaoEncontradoException:
            raise UsuarioNaoEncontradoException(f"Usuário não encontrado.")
        
        if usuario.status == StatusUsuario.BLOQUEADO:
            raise UsuarioBloqueadoException(f"Usuário Bloqueado. Empréstimo Negado.")
        
        # Integração com Módulo de Catálogo (IT-001, IT-003)
        try:
            livro = self._modulo_catalogo.obter_livro(isbn_livro)
        except LivroNaoEncontradoException:
            raise LivroNaoEncontradoException(f"Livro não encontrado.")
        
        if not self._modulo_catalogo.verificar_disponibilidade(isbn_livro):
            raise LivroIndisponvelException(f"Livro Indisponível. Estoque Zero.")
        
        # Verifica se o usuário já tem um empréstimo ativo do mesmo livro (IT-004)
        for emprestimo in self._emprestimos.values():
            if (emprestimo.matricula_usuario == matricula_usuario and 
                emprestimo.isbn_livro == isbn_livro and 
                emprestimo.status == StatusEmprestimo.ATIVO):
                raise EmprestimoJaExisteException(f"Livro já emprestado ao usuário.")
        
        # Registra o empréstimo
        self._contador_emprestimos += 1
        id_emprestimo = f"EMP-{self._contador_emprestimos:05d}"
        
        data_emprestimo = datetime.now()
        data_devolucao_prevista = data_emprestimo + timedelta(days=dias_emprestimo)
        
        emprestimo = Emprestimo(
            id_emprestimo=id_emprestimo,
            matricula_usuario=matricula_usuario,
            isbn_livro=isbn_livro,
            data_emprestimo=data_emprestimo,
            data_devolucao_prevista=data_devolucao_prevista
        )
        
        self._emprestimos[id_emprestimo] = emprestimo
        
        # Atualiza o módulo de catálogo (decrementa estoque)
        self._modulo_catalogo.decrementar_estoque(isbn_livro)
        
        # Atualiza o módulo de usuários (incrementa empréstimos ativos)
        self._modulo_usuarios.incrementar_emprestimos(matricula_usuario)
        
        return emprestimo

    def registrar_devolucao(self, id_emprestimo: str) -> Emprestimo:
        """
        Registra a devolução de um livro.
        
        Integração com Módulo de Catálogo:
            - Incrementa o estoque do livro.
        
        Integração com Módulo de Usuários:
            - Decrementa o contador de empréstimos do usuário.
        
        Args:
            id_emprestimo: ID do empréstimo.
        
        Returns:
            Emprestimo: O empréstimo com devolução registrada.
        
        Raises:
            EmprestimoNaoEncontradoException: Se o empréstimo não existe.
        """
        if id_emprestimo not in self._emprestimos:
            raise EmprestimoNaoEncontradoException(f"Empréstimo '{id_emprestimo}' não encontrado.")
        
        emprestimo = self._emprestimos[id_emprestimo]
        
        if emprestimo.status != StatusEmprestimo.ATIVO:
            raise ValidacaoException(f"Empréstimo '{id_emprestimo}' não está ativo.")
        
        emprestimo.data_devolucao_real = datetime.now()
        emprestimo.status = StatusEmprestimo.DEVOLVIDO
        
        # Atualiza o módulo de catálogo (incrementa estoque)
        self._modulo_catalogo.incrementar_estoque(emprestimo.isbn_livro)
        
        # Atualiza o módulo de usuários (decrementa empréstimos ativos)
        self._modulo_usuarios.decrementar_emprestimos(emprestimo.matricula_usuario)
        
        return emprestimo

    def obter_emprestimo(self, id_emprestimo: str) -> Emprestimo:
        """
        Obtém um empréstimo pelo ID.
        
        Args:
            id_emprestimo: ID do empréstimo.
        
        Returns:
            Emprestimo: O empréstimo encontrado.
        
        Raises:
            EmprestimoNaoEncontradoException: Se o empréstimo não existe.
        """
        if id_emprestimo not in self._emprestimos:
            raise EmprestimoNaoEncontradoException(f"Empréstimo '{id_emprestimo}' não encontrado.")
        
        return self._emprestimos[id_emprestimo]

    def listar_emprestimos(self) -> List[Emprestimo]:
        """
        Lista todos os empréstimos.
        
        Returns:
            List[Emprestimo]: Lista de empréstimos.
        """
        return list(self._emprestimos.values())

    def listar_emprestimos_ativos(self) -> List[Emprestimo]:
        """
        Lista todos os empréstimos ativos.
        
        Returns:
            List[Emprestimo]: Lista de empréstimos ativos.
        """
        return [e for e in self._emprestimos.values() if e.status == StatusEmprestimo.ATIVO]

    def listar_emprestimos_por_usuario(self, matricula_usuario: str) -> List[Emprestimo]:
        """
        Lista todos os empréstimos de um usuário.
        
        Args:
            matricula_usuario: Matrícula do usuário.
        
        Returns:
            List[Emprestimo]: Lista de empréstimos do usuário.
        """
        return [e for e in self._emprestimos.values() if e.matricula_usuario == matricula_usuario]

    def listar_emprestimos_por_livro(self, isbn_livro: str) -> List[Emprestimo]:
        """
        Lista todos os empréstimos de um livro.
        
        Args:
            isbn_livro: ISBN do livro.
        
        Returns:
            List[Emprestimo]: Lista de empréstimos do livro.
        """
        return [e for e in self._emprestimos.values() if e.isbn_livro == isbn_livro]