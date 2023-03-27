import tkinter as tk
import brailleTable
    
class brailleButton:
    def __init__(self, character, id):
        self.button = tk.Button(character, text = str(id), command = self.switchState, width = 10, height = 5)
        self.state = False
        self.character = character
    def switchState(self):
        if self.state:
            self.state = False
            self.button.configure(relief = tk.RAISED)
        else:
            self.state = True
            self.button.configure(relief = tk.SUNKEN)
        self.character.update()

class brailleCharacter(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.brailleButtons = list(brailleButton(self, i + 1) for i in range(6))
        self.output = ""
        self.display = tk.Label(self, text="?")
        
        for col in range(2):
            for row in range(3):
                self.brailleButtons[col * 3 + row].button.grid(column = col, row = row)
        self.display.grid(column = 0, row = 3, columnspan = 2)

    def update(self):
        self.output = ""
        for button in self.brailleButtons:
            if button.state:
                self.output += "1"
            else:
                self.output += "0"
        
        value = brailleTable.brailleTable.get(self.output)
        if value:
            self.display.configure(text = value)
        else:
            self.display.configure(text = "?")

def run():
    myWindow = tk.Tk()
    myWindow.title("BrailleTranslate")
    brailleCharacter(myWindow).grid()
    myWindow.mainloop()
run()