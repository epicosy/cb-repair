
import inspect
import types


# source: Python Cookbook, 3rd Edition. 2013 9.20 Implementing Multiple Dispatch with Function Annotations
class MultiMethod:
    """
        represents a single multi-method
    """
    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        """
            register a new method as a multi-method
        """

        sig = inspect.signature(meth)

        # Build a type signature from the method's annotations
        types = []

        for name, parm in sig.parameters.items():
            if name == 'self':
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(f"Argument {name} must be annotated with a type")
            if not isinstance(parm.annotation, type):
                raise TypeError(f"Argument {name} annotation must be a type")
            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth
            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        """
        Call a method based on type signature of the arguments
        """
        types = tuple(type(arg) for arg in args[1:])
        meth = self._methods.get(types, None)

        if meth:
            return meth(*args)
        else:
            raise TypeError(f"No matching method for types {types}")

    def __get__(self, instance, cls):
        """
        Descriptor method needed to make calls work in a class
        """
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self


class MultiDict(dict):
    """
    Special dictionary to build multimethods in a metaclass
    """
    def __setitem__(self, key, value):
        if key in self:
            # If key already exists, it must be a multimethod or callable
            current_value = self[key]
            if isinstance(current_value, MultiMethod):
                current_value.register(value)
            else:
                mvalue = MultiMethod(key)
                mvalue.register(current_value)
                mvalue.register(value)
                super().__setitem__(key, mvalue)
        else:
            super().__setitem__(key, value)


class MultipleMeta(type):
    """
    Metaclass that allows multiple dispatch of methods
    """

    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()
