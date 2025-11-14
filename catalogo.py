"""
Módulo de Catálogo de Livros (Equipe 2)
Responsável pelo cadastro de livros, autores, estoque e status.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import sys
sys.path.insert(0, '/home/ubuntu/sgbu_python')

from utils.excecoes import (
    LivroNaoEncontradoException,
    ValidacaoException,
    EstoqueInsuficienteException
)


class StatusLivro(Enum):
    """Enum para status de livros."""
    DISPONIVEL = "Disponível"
    EMPRESTADO = "Emprestado"
    RESERVADO = "Reservado"


@dataclass
class Livro:
    """Classe que representa um livro no catálogo."""
    isbn: str
    titulo: str
    autor: str
    estoque: int
    status: StatusLivro = StatusLivro.DISPONIVEL
    editora: Optional[str] = None
    ano_publicacao: Optional[int] = None

    def __post_init__(self):
        """Valida os dados do livro após a inicialização."""
        self._validar()

    def _validar(self):
        """Valida os dados do livro."""
        if not self.isbn or not isinstance(self.isbn, str):
            raise ValidacaoException("ISBN é obrigatório e deve ser uma string.")
        
        if not self.titulo or not isinstance(self.titulo, str):
            raise ValidacaoException("Título é obrigatório e deve ser uma string.")
        
        if not self.autor or not isinstance(self.autor, str):
            raise ValidacaoException("Autor é obrigatório e deve ser uma string.")
        
        if not isinstance(self.estoque, int) or self.estoque < 0:
            raise ValidacaoException("Estoque deve ser um número inteiro não-negativo.")

    def to_dict(self):
        """Serializa o livro para um dicionário (contrato de serialização)."""
        return {
            "isbn": self.isbn,
            "titulo": self.titulo,
            "autor": self.autor,
            "estoque": self.estoque,
            "status": self.status.value,
            "editora": self.editora,
            "ano_publicacao": self.ano_publicacao
        }


class ModuloCatalogo:
    """
    Módulo responsável pelo gerenciamento do catálogo de livros.
    Implementa CRUD e controle de estoque.
    """

    def __init__(self):
        """Inicializa o módulo com um dicionário vazio de livros."""
        self._livros: dict[str, Livro] = {}

    def cadastrar_livro(self, isbn: str, titulo: str, autor: str, estoque: int, 
                       editora: Optional[str] = None, ano_publicacao: Optional[int] = None) -> Livro:
        """
        Cadastra um novo livro no catálogo.
        
        Args:
            isbn: ISBN único do livro.
            titulo: Título do livro.
            autor: Autor do livro.
            estoque: Quantidade de cópias em estoque.
            editora: Editora do livro (opcional).
            ano_publicacao: Ano de publicação (opcional).
        
        Returns:
            Livro: O livro cadastrado.
        
        Raises:
            ValidacaoException: Se os dados são inválidos.
        """
        if isbn in self._livros:
            raise ValidacaoException(f"Livro com ISBN '{isbn}' já existe no catálogo.")
        
        livro = Livro(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            estoque=estoque,
            editora=editora,
            ano_publicacao=ano_publicacao
        )
        
        self._livros[isbn] = livro
        return livro

    def obter_livro(self, isbn: str) -> Livro:
        """
        Obtém um livro pelo ISBN.
        
        Args:
            isbn: ISBN do livro.
        
        Returns:
            Livro: O livro encontrado.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
        """
        if isbn not in self._livros:
            raise LivroNaoEncontradoException(f"Livro com ISBN '{isbn}' não encontrado no catálogo.")
        
        return self._livros[isbn]

    def listar_livros(self) -> List[Livro]:
        """
        Lista todos os livros cadastrados.
        
        Returns:
            List[Livro]: Lista de livros.
        """
        return list(self._livros.values())

    def editar_livro(self, isbn: str, titulo: Optional[str] = None, autor: Optional[str] = None,
                    editora: Optional[str] = None, ano_publicacao: Optional[int] = None) -> Livro:
        """
        Edita os dados de um livro existente.
        
        Args:
            isbn: ISBN do livro.
            titulo: Novo título (opcional).
            autor: Novo autor (opcional).
            editora: Nova editora (opcional).
            ano_publicacao: Novo ano de publicação (opcional).
        
        Returns:
            Livro: O livro editado.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
        """
        livro = self.obter_livro(isbn)
        
        if titulo is not None:
            livro.titulo = titulo
        
        if autor is not None:
            livro.autor = autor
        
        if editora is not None:
            livro.editora = editora
        
        if ano_publicacao is not None:
            livro.ano_publicacao = ano_publicacao
        
        return livro

    def remover_livro(self, isbn: str) -> bool:
        """
        Remove um livro do catálogo.
        
        Args:
            isbn: ISBN do livro.
        
        Returns:
            bool: True se removido com sucesso.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
        """
        livro = self.obter_livro(isbn)
        del self._livros[isbn]
        return True

    def verificar_disponibilidade(self, isbn: str) -> bool:
        """
        Verifica se um livro está disponível (estoque > 0).
        
        Args:
            isbn: ISBN do livro.
        
        Returns:
            bool: True se disponível, False caso contrário.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
        """
        livro = self.obter_livro(isbn)
        return livro.estoque > 0

    def decrementar_estoque(self, isbn: str) -> int:
        """
        Decrementa o estoque de um livro (após empréstimo).
        
        Args:
            isbn: ISBN do livro.
        
        Returns:
            int: O novo estoque.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
            EstoqueInsuficienteException: Se o estoque é zero.
        """
        livro = self.obter_livro(isbn)
        
        if livro.estoque <= 0:
            raise EstoqueInsuficienteException(f"Livro '{isbn}' está com estoque insuficiente.")
        
        livro.estoque -= 1
        return livro.estoque

    def incrementar_estoque(self, isbn: str) -> int:
        """
        Incrementa o estoque de um livro (após devolução).
        
        Args:
            isbn: ISBN do livro.
        
        Returns:
            int: O novo estoque.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
        """
        livro = self.obter_livro(isbn)
        livro.estoque += 1
        return livro.estoque

    def atualizar_status(self, isbn: str, novo_status: str) -> Livro:
        """
        Atualiza o status de um livro.
        
        Args:
            isbn: ISBN do livro.
            novo_status: Novo status (Disponível, Emprestado, Reservado).
        
        Returns:
            Livro: O livro com status atualizado.
        
        Raises:
            LivroNaoEncontradoException: Se o livro não existe.
            ValidacaoException: Se o status é inválido.
        """
        livro = self.obter_livro(isbn)
        
        try:
            status_enum = StatusLivro[novo_status.upper()] if isinstance(novo_status, str) else novo_status
        except (KeyError, AttributeError):
            raise ValidacaoException(f"Status inválido: {novo_status}. Deve ser um dos: {[s.name for s in StatusLivro]}")
        
        livro.status = status_enum
        return livro

    def listar_por_autor(self, autor: str) -> List[Livro]:
        """
        Lista todos os livros de um autor específico.
        
        Args:
            autor: Nome do autor.
        
        Returns:
            List[Livro]: Lista de livros do autor.
        """
        return [livro for livro in self._livros.values() if livro.autor.lower() == autor.lower()]