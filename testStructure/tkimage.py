import Tkinter

root = Tkinter.Tk()

canvas = Tkinter.Canvas(root)

canvas.grid(row = 0, column = 0)

photo = Tkinter.PhotoImage(file = './Idle3.gif')

canvas.create_image(20,20, image=photo)

root.mainloop()

