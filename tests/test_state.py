import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Optional, Any
from quillion.components import State, StateMeta


class TestStateMeta:
    def test_metaclass_initialization_no_defaults(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                def method(self):
                    pass
                
                @classmethod
                def class_method(cls):
                    pass
                
                @staticmethod
                def static_method():
                    pass
                
                @property
                def computed(self):
                    return "computed"
            
            assert TestState._defaults == {}
    
    def test_metaclass_initialization_with_validation(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class ValidState(metaclass=StateMeta):
                count: int = 0
                name: str = "test"
            
            assert ValidState._defaults == {"count": 0, "name": "test"}
    
    def test_metaclass_initialization_validation_error(self):
        with patch('quillion.core.app.Quillion._instance', None):
            with pytest.raises(TypeError) as exc_info:
                class InvalidState(metaclass=StateMeta):
                    count: int = "not_an_int"
            
            assert "Invalid default values in State class" in str(exc_info.value)
    
    def test_metaclass_getattr_delegation(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                value: int = 42
        
        mock_instance = Mock()
        mock_instance.value = 42
        
        with patch.object(TestState, 'get_instance', return_value=mock_instance):
            result = TestState.value
            
            assert result == 42
            TestState.get_instance.assert_called_once()
    
    def test_get_instance_creation(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                value: int = 10
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            
            assert TestState in mock_app._state_instances
            assert isinstance(mock_app._state_instances[TestState], State)
            assert instance is mock_app._state_instances[TestState]
    
    def test_get_instance_existing(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                value: int = 10
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        
        state_instance = State(TestState)
        mock_app._state_instances = {TestState: state_instance}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            
            assert instance is state_instance
    
    def test_get_instance_no_websocket(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                value: int = 10
        
        mock_app = Mock()
        mock_app.websocket = None
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            with pytest.raises(RuntimeError) as exc_info:
                TestState.get_instance()
            
            assert "No active WebSocket connection for state access" in str(exc_info.value)
    
    def test_get_instance_no_app(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                value: int = 10
        
        with patch('quillion.core.app.Quillion._instance', None):
            with pytest.raises(RuntimeError) as exc_info:
                TestState.get_instance()
            
            assert "No active WebSocket connection for state access" in str(exc_info.value)
    
    def test_set_method_updates_state(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                count: int = 0
                name: str = "initial"
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            
            TestState.set(count=5, name="updated")
            
            assert instance._data["count"] == 5
            assert instance._data["name"] == "updated"
    
    def test_set_method_validation(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                count: int = 0
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            TestState.get_instance()
            
            with pytest.raises(TypeError) as exc_info:
                TestState.set(count="not_an_int")
            
            assert "Invalid value for state variable 'count'" in str(exc_info.value)
    
    def test_set_method_triggers_rerender(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                count: int = 0
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            mock_callback = Mock()
            instance._rerender_callback = mock_callback
            
            TestState.set(count=1)
            
            mock_callback.assert_called_once()
    
    def test_set_method_no_rerender_same_value(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                count: int = 0
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            mock_callback = Mock()
            instance._rerender_callback = mock_callback
            
            TestState.set(count=0)
            
            mock_callback.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_set_method_async_rerender(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                count: int = 0
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = TestState.get_instance()
            
            async_called = False
            
            async def async_callback():
                nonlocal async_called
                async_called = True
            
            instance._rerender_callback = async_callback
            
            TestState.set(count=1)
            
            await asyncio.sleep(0.01)
            assert async_called


class TestState:
    def test_state_initialization(self):
        class TestStateClass:
            _defaults = {"count": 0, "name": "test"}
        
        state = State(TestStateClass)
        
        assert state._cls == TestStateClass
        assert state._data == {"count": 0, "name": "test"}
        assert state._rerender_callback is None
    
    def test_state_getattr_existing(self):
        class TestStateClass:
            _defaults = {"value": 42}
        
        state = State(TestStateClass)
        
        assert state.value == 42
    
    def test_state_getattr_missing(self):
        class TestStateClass:
            _defaults = {"value": 42}
        
        state = State(TestStateClass)
        
        with pytest.raises(AttributeError):
            _ = state.nonexistent
    
    def test_state_getattr_inherited(self):
        class TestStateClass:
            _defaults = {}
        
        state = State(TestStateClass)
        
        assert hasattr(state, '_rerender_callback')
        assert state._rerender_callback is None
    
    def test_set_rerender_callback(self):
        class TestStateClass:
            _defaults = {}
        
        state = State(TestStateClass)
        
        def callback():
            pass
        
        state._set_rerender_callback(callback)
        
        assert state._rerender_callback == callback


class TestStateIntegration:
    def test_complete_state_workflow(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class CounterState(metaclass=StateMeta):
                count: int = 0
                name: str = "counter"
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance1 = CounterState.get_instance()
            assert instance1.count == 0
            assert instance1.name == "counter"
            
            CounterState.set(count=5, name="updated")
            
            assert instance1._data["count"] == 5
            assert instance1._data["name"] == "updated"
            
            instance2 = CounterState.get_instance()
            assert instance2 is instance1
    
    def test_multiple_state_classes(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class UserState(metaclass=StateMeta):
                name: str = "user"
                logged_in: bool = False
            
            class AppState(metaclass=StateMeta):
                theme: str = "light"
                language: str = "en"
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            user_instance = UserState.get_instance()
            app_instance = AppState.get_instance()
            
            assert user_instance is not app_instance
            assert UserState in mock_app._state_instances
            assert AppState in mock_app._state_instances
            
            UserState.set(name="admin")
            AppState.set(theme="dark")
            
            assert user_instance._data["name"] == "admin"
            assert app_instance._data["theme"] == "dark"
            assert user_instance._data["logged_in"] == False
            assert app_instance._data["language"] == "en"
    
    def test_state_with_complex_types(self):
        from typing import List, Dict
        
        with patch('quillion.core.app.Quillion._instance', None):
            class ComplexState(metaclass=StateMeta):
                items: List[str] = ["a", "b", "c"]
                settings: Dict[str, Any] = {"key": "value"}
                optional_value: Optional[int] = None
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = ComplexState.get_instance()
            
            assert instance._data["items"] == ["a", "b", "c"]
            assert instance._data["settings"] == {"key": "value"}
            assert instance._data["optional_value"] is None
            
            ComplexState.set(items=["x", "y"], settings={"new": "data"})
            
            assert instance._data["items"] == ["x", "y"]
            assert instance._data["settings"] == {"new": "data"}


class TestStateEdgeCases:
    def test_state_with_no_annotations(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class NoAnnotationState(metaclass=StateMeta):
                value = "default"
            
            assert NoAnnotationState._defaults == {"value": "default"}
    
    def test_state_with_methods(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class StateWithMethods(metaclass=StateMeta):
                value: int = 0
                
                def get_double(self):
                    return self.value * 2
                
                @classmethod
                def class_method(cls):
                    return "class"
                
                @staticmethod
                def static_method():
                    return "static"
            
            assert StateWithMethods._defaults == {"value": 0}
            assert hasattr(StateWithMethods, "get_double")
            assert hasattr(StateWithMethods, "class_method")
            assert hasattr(StateWithMethods, "static_method")
    
    def test_state_empty_defaults(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class EmptyState(metaclass=StateMeta):
                pass
            
            assert EmptyState._defaults == {}
    
    def test_state_private_attributes(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class PrivateState(metaclass=StateMeta):
                _private: int = 42
                public: int = 100
            
            assert PrivateState._defaults == {"public": 100}
    
    def test_set_nonexistent_attribute(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class TestState(metaclass=StateMeta):
                existing: int = 0
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            TestState.get_instance()
            
            TestState.set(nonexistent="value")
            
            instance = TestState.get_instance()
            with pytest.raises(AttributeError):
                _ = instance.nonexistent


class TestStateValidation:
    def test_validation_with_pydantic_types(self):
        from pydantic import conint, constr
        
        with patch('quillion.core.app.Quillion._instance', None):
            class ValidatedState(metaclass=StateMeta):
                positive: conint(gt=0) = 1
                short_string: constr(max_length=5) = "short"
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = ValidatedState.get_instance()
            
            ValidatedState.set(positive=5, short_string="abc")
            assert instance._data["positive"] == 5
            assert instance._data["short_string"] == "abc"
            
            with pytest.raises(TypeError):
                ValidatedState.set(positive=-1)
            
            with pytest.raises(TypeError):
                ValidatedState.set(short_string="too_long")
    
    def test_validation_optional_values(self):
        from typing import Optional
        
        with patch('quillion.core.app.Quillion._instance', None):
            class OptionalState(metaclass=StateMeta):
                value: Optional[int] = None
        
        mock_app = Mock()
        mock_app.websocket = Mock()
        mock_app._state_instances = {}
        
        with patch('quillion.core.app.Quillion._instance', mock_app):
            instance = OptionalState.get_instance()
            
            OptionalState.set(value=None)
            assert instance._data["value"] is None
            
            OptionalState.set(value=42)
            assert instance._data["value"] == 42
            
            with pytest.raises(TypeError):
                OptionalState.set(value="not_int")


class TestStateBehavior:
    def test_state_data_isolation(self):
        class StateClass1:
            _defaults = {"value": 1}
        
        class StateClass2:
            _defaults = {"value": 2}
        
        state1 = State(StateClass1)
        state2 = State(StateClass2)
        
        assert state1._data == {"value": 1}
        assert state2._data == {"value": 2}
        
        state1._data["value"] = 10
        assert state2._data["value"] == 2


class TestStateSimple:
    def test_state_creation_and_access(self):
        with patch('quillion.core.app.Quillion._instance', None):
            class SimpleState(metaclass=StateMeta):
                number: int = 42
                text: str = "hello"
        
        state_instance = State(SimpleState)
        
        assert state_instance.number == 42
        assert state_instance.text == "hello"
        
        assert state_instance._data == {"number": 42, "text": "hello"}
