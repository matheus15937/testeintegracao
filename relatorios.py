"""
Módulo de Geração de Relatórios (Equipe 4)
Responsável pela geração de relatórios simples de uso da biblioteca.
Depende dos dados dos outros módulos.
"""

from typing import List, Dict, Any
from datetime import datetime
import sys
sys.path.insert(0, '/home/ubuntu/sgbu_python')

from modulos.usuarios import ModuloUsuarios
from modulos.catalogo import ModuloCatalogo
from modulos.emprestimo import ModuloEmprestimo, StatusEmprestimo


class ModuloRelatorios:
    """
    Módulo responsável pela geração de relatórios.
    Integra-se com os módulos de Usuários, Catálogo e Empréstimo.
    """

    def __init__(self, modulo_usuarios: ModuloUsuarios, modulo_catalogo: ModuloCatalogo, modulo_emprestimo: ModuloEmprestimo):
        """
        Inicializa o módulo de relatórios.
        
        Args:
            modulo_usuarios: Referência ao módulo de usuários.
            modulo_catalogo: Referência ao módulo de catálogo.
            modulo_emprestimo: Referência ao módulo de empréstimo.
        """
        self._modulo_usuarios = modulo_usuarios
        self._modulo_catalogo = modulo_catalogo
        self._modulo_emprestimo = modulo_emprestimo

    def relatorio_livros_mais_emprestados(self, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Gera um relatório dos livros mais emprestados.
        
        Returns:
            List[Dict]: Lista com informações dos livros mais emprestados.
        """
        contagem_emprestimos: Dict[str, int] = {}
        
        for emprestimo in self._modulo_emprestimo.listar_emprestimos():
            isbn = emprestimo.isbn_livro
            contagem_emprestimos[isbn] = contagem_emprestimos.get(isbn, 0) + 1
        
        # Ordena por quantidade de empréstimos (descendente)
        livros_ordenados = sorted(contagem_emprestimos.items(), key=lambda x: x[1], reverse=True)[:limite]
        
        resultado = []
        for isbn, quantidade in livros_ordenados:
            try:
                livro = self._modulo_catalogo.obter_livro(isbn)
                resultado.append({
                    "isbn": isbn,
                    "titulo": livro.titulo,
                    "autor": livro.autor,
                    "quantidade_emprestimos": quantidade
                })
            except:
                pass
        
        return resultado

    def relatorio_usuarios_mais_ativos(self, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Gera um relatório dos usuários mais ativos (mais empréstimos).
        
        Returns:
            List[Dict]: Lista com informações dos usuários mais ativos.
        """
        contagem_emprestimos: Dict[str, int] = {}
        
        for emprestimo in self._modulo_emprestimo.listar_emprestimos():
            matricula = emprestimo.matricula_usuario
            contagem_emprestimos[matricula] = contagem_emprestimos.get(matricula, 0) + 1
        
        # Ordena por quantidade de empréstimos (descendente)
        usuarios_ordenados = sorted(contagem_emprestimos.items(), key=lambda x: x[1], reverse=True)[:limite]
        
        resultado = []
        for matricula, quantidade in usuarios_ordenados:
            try:
                usuario = self._modulo_usuarios.obter_usuario(matricula)
                resultado.append({
                    "matricula": matricula,
                    "nome": usuario.nome,
                    "tipo": usuario.tipo.value,
                    "quantidade_emprestimos": quantidade
                })
            except:
                pass
        
        return resultado

    def relatorio_emprestimos_ativos(self) -> List[Dict[str, Any]]:
        """
        Gera um relatório dos empréstimos ativos.
        
        Returns:
            List[Dict]: Lista com informações dos empréstimos ativos.
        """
        resultado = []
        
        for emprestimo in self._modulo_emprestimo.listar_emprestimos_ativos():
            try:
                usuario = self._modulo_usuarios.obter_usuario(emprestimo.matricula_usuario)
                livro = self._modulo_catalogo.obter_livro(emprestimo.isbn_livro)
                
                resultado.append({
                    "id_emprestimo": emprestimo.id_emprestimo,
                    "usuario": usuario.nome,
                    "livro": livro.titulo,
                    "data_emprestimo": emprestimo.data_emprestimo.isoformat(),
                    "data_devolucao_prevista": emprestimo.data_devolucao_prevista.isoformat(),
                    "dias_restantes": (emprestimo.data_devolucao_prevista - datetime.now()).days
                })
            except:
                pass
        
        return resultado

    def relatorio_acervo(self) -> Dict[str, Any]:
        """
        Gera um relatório geral do acervo.
        
        Returns:
            Dict: Informações gerais do acervo.
        """
        livros = self._modulo_catalogo.listar_livros()
        
        total_livros = len(livros)
        total_copias = sum(livro.estoque for livro in livros)
        livros_indisponveis = sum(1 for livro in livros if livro.estoque == 0)
        
        return {
            "total_titulos": total_livros,
            "total_copias_disponiveis": total_copias,
            "livros_indisponveis": livros_indisponveis,
            "data_geracao": datetime.now().isoformat()
        }

    def relatorio_usuarios(self) -> Dict[str, Any]:
        """
        Gera um relatório geral de usuários.
        
        Returns:
            Dict: Informações gerais de usuários.
        """
        usuarios = self._modulo_usuarios.listar_usuarios()
        
        total_usuarios = len(usuarios)
        usuarios_ativos = sum(1 for u in usuarios if u.status.value == "Ativo")
        usuarios_bloqueados = sum(1 for u in usuarios if u.status.value == "Bloqueado")
        
        return {
            "total_usuarios": total_usuarios,
            "usuarios_ativos": usuarios_ativos,
            "usuarios_bloqueados": usuarios_bloqueados,
            "data_geracao": datetime.now().isoformat()
        }