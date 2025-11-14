"""
Módulo de Exceções Customizadas para o SGBU.
Define as exceções específicas do sistema.
"""


class SGBUException(Exception):
    """Exceção base para o SGBU."""
    pass


class UsuarioNaoEncontradoException(SGBUException):
    """Lançada quando um usuário não é encontrado."""
    pass


class UsuarioBloqueadoException(SGBUException):
    """Lançada quando um usuário está bloqueado."""
    pass


class LivroNaoEncontradoException(SGBUException):
    """Lançada quando um livro não é encontrado."""
    pass


class LivroIndisponvelException(SGBUException):
    """Lançada quando um livro está indisponível (estoque zero)."""
    pass


class EstoqueInsuficienteException(SGBUException):
    """Lançada quando o estoque é insuficiente."""
    pass


class EmprestimoJaExisteException(SGBUException):
    """Lançada quando um empréstimo já existe para o mesmo livro e usuário."""
    pass


class EmprestimoNaoEncontradoException(SGBUException):
    """Lançada quando um empréstimo não é encontrado."""
    pass


class ValidacaoException(SGBUException):
    """Lançada quando há erro de validação de dados."""
    pass


class UsuarioPossuiEmprestimosAtivosException(SGBUException):
    """Lançada quando um usuário possui empréstimos ativos e não pode ser removido."""
    pass