vlan = int(input("Ingrese el número de VLAN: "))

if vlan >= 1 and vlan <= 1005:
    print("La VLAN corresponde al rango normal.")
elif vlan >= 1006 and vlan <= 4094:
    print("La VLAN corresponde al rango extendido.")
else:
    print("El número ingresado no corresponde a una VLAN válida.")