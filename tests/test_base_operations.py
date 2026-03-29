import unittest

from tests.test_web_base import TestWebBase


class TestBaseOperations(TestWebBase):
    """Direct unit tests for BaseOperations.set_input_from_dict."""

    def _make_concrete(self, **attrs):
        """Return a minimal concrete subclass instance with the given initial attributes."""
        from hedweb.base_operations import BaseOperations

        class ConcreteOp(BaseOperations):
            def process(self):
                return {}

        obj = ConcreteOp()
        for k, v in attrs.items():
            object.__setattr__(obj, k, v)
        return obj

    def test_set_known_attributes(self):
        obj = self._make_concrete(alpha=1, beta="hello")
        obj.set_input_from_dict({"alpha": 99, "beta": "world"})
        self.assertEqual(obj.alpha, 99)
        self.assertEqual(obj.beta, "world")

    def test_unknown_attributes_ignored(self):
        obj = self._make_concrete(alpha=1)
        obj.set_input_from_dict({"alpha": 2, "gamma": "should_not_be_set"})
        self.assertEqual(obj.alpha, 2)
        self.assertFalse(hasattr(obj, "gamma"), "unknown keys must not be injected as new attributes")

    def test_callable_attributes_not_overwritten(self):
        def original():
            return "original"

        obj = self._make_concrete()
        # Manually attach a callable attribute
        obj.my_method = original
        obj.set_input_from_dict({"my_method": "replacement_string"})
        self.assertTrue(callable(obj.my_method), "callable attribute must not be overwritten")
        self.assertEqual(obj.my_method(), "original")

    def test_private_attributes_not_set(self):
        obj = self._make_concrete(_secret="initial")
        obj.set_input_from_dict({"_secret": "injected"})
        self.assertEqual(obj._secret, "initial", "private attributes must not be overwritten via set_input_from_dict")

    def test_none_value_allowed(self):
        obj = self._make_concrete(schema=None, command="validate")
        obj.set_input_from_dict({"schema": None, "command": None})
        self.assertIsNone(obj.schema)
        self.assertIsNone(obj.command)

    def test_empty_dict_is_noop(self):
        obj = self._make_concrete(alpha=42)
        obj.set_input_from_dict({})
        self.assertEqual(obj.alpha, 42)

    def test_process_is_abstract(self):
        from hedweb.base_operations import BaseOperations

        with self.assertRaises(TypeError):
            BaseOperations()  # cannot instantiate without implementing process()


if __name__ == "__main__":
    unittest.main()
