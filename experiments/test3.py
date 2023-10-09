class Example:
    def __init__(self):
        self._some_attribute = "Instance variable"

    @property
    def some_attribute(self):
        return self._some_attribute

    @some_attribute.setter
    def some_attribute(self, value):
        print(f"setter {value} called")
        self._some_attribute = value


# Create an object of the class
obj = Example()

# Access the attribute/method
print(obj.some_attribute)  # This will print "Instance variable"
obj.some_attribute = "New value"
print(obj.some_attribute)  
