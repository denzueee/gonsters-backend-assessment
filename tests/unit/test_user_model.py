"""
Additional tests for User model to increase coverage
"""

import pytest
from app.models import User


@pytest.mark.unit
class TestUserModelAdditional:
    """Additional tests for User model edge cases and methods"""
    
    def test_user_repr(self, db_session):
        """Test User __repr__ method"""
        user = User(
            username='testuser',
            email='test@example.com',
            role='Operator'
        )
        user.set_password('TestPass123!')
        db_session.add(user)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(user)
        assert 'testuser' in repr_str
        assert 'Operator' in repr_str
        assert repr_str == '<User testuser (Operator)>'
    
    def test_user_to_dict_without_permissions(self, db_session):
        """Test User.to_dict() without including permissions"""
        user = User(
            username='dictuser',
            email='dict@example.com',
            role='Supervisor',
            factory_id='factory-123',
            department='Engineering'
        )
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        # Test to_dict without permissions
        user_dict = user.to_dict(include_permissions=False)
        assert 'permissions' not in user_dict
        assert user_dict['username'] == 'dictuser'
        assert user_dict['role'] == 'Supervisor'
        assert user_dict['factory_id'] == 'factory-123'
        assert user_dict['department'] == 'Engineering'
    
    def test_user_to_dict_with_permissions(self, db_session):
        """Test User.to_dict() with permissions included"""
        user = User(
            username='permuser',
            email='perm@example.com',
            role='Management'
        )
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        # Test to_dict with permissions
        user_dict = user.to_dict(include_permissions=True)
        assert 'permissions' in user_dict
        assert 'read:config' in user_dict['permissions']
        assert 'write:config' in user_dict['permissions']
    
    def test_user_get_permissions_operator(self, db_session):
        """Test get_permissions for Operator role"""
        user = User(username='op', email='op@example.com', role='Operator')
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        perms = user.get_permissions()
        assert 'read:machines' in perms
        assert 'read:sensor_data' in perms
        assert 'write:sensor_data' in perms
        assert 'read:config' not in perms  # Operator doesn't have this
    
    def test_user_has_permission_true(self, db_session):
        """Test has_permission returns True for valid permission"""
        user = User(username='su', email='su@example.com', role='Supervisor')
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        assert user.has_permission('read:reports') is True
        assert user.has_permission('write:reports') is True
    
    def test_user_has_permission_false(self, db_session):
        """Test has_permission returns False for invalid permission"""
        user = User(username='op2', email='op2@example.com', role='Operator')
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        # Operator doesn't have these permissions
        assert user.has_permission('delete:machines') is False
        assert user.has_permission('write:config') is False
