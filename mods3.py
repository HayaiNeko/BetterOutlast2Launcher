


class Person:
    persons = []

    def __init__(self, name):
        self.name = name
        self.__class__.persons.append(self)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Person):
            return self.name == other.name
        return False

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def test(cls, selected_persons):
        for person in cls.persons:
            if person in selected_persons:
                print(f"{person} is in selected_persons.")
            else:
                print(f"{person} not in selected_persons")


if __name__ == "__main__":
    Person("Pierre")
    Person("Jean")
    Person("Luc")
    Person("Aubin")
    Person("Eline")
    Person("Gabi")
    Person("<3")

    selected_persons = set()
    selected_persons.add("Eline")
    selected_persons.add("Gabi")

    Person.test(selected_persons)