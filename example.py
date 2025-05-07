

alist = [1,6,3,8,9,2,4]

alist.sort()

print(alist)


class Person():

    def __init__(self, name, friends):
        self.name= name
        self.friends = friends


person1 = Person(name="Paul", friends=4)
person2 = Person(name="Peter", friends=2)
person3 = Person(name="Pedro", friends=8)

people = [person1, person2, person3]

people.sort(key= lambda person : person.friends, reverse=True )

print("Most popular")
for person in people:
    print(person.name + " " + str(person.friends))



#lambda : Anonamous functions
#Syntax
#lambda parameters : expression