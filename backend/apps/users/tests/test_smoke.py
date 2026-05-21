"""Smoke test — valida apenas que pytest+django+conftest fixtures funcionam.
Deve ser apagado depois que outros testes substanciais existirem."""


def test_pytest_django_wired(reader_user):
    assert reader_user.id is not None
    assert reader_user.email == 'leitor@interpop.test'


def test_role_fixtures_distinct(dev_user, admin_user, editor_user, reader_user):
    roles = {dev_user.role, admin_user.role, editor_user.role, reader_user.role}
    assert len(roles) == 4
