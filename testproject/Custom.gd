extends Node2D

export(int) var age
export(String) var fullname
export(String) var catchphrase
export(Array, String, MULTILINE) var dialogue

func _ready():
	print(tr("Hello from script"))
