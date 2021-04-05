#!/usr/bin/env python
import PySimpleGUI as sg

reverse = {}
colorhex = {}

colors = {
    "abbey"                     : ( 76,  79,  86),
    "acadia"                    : ( 27,  20,   4),
    "acapulco"                  : (124, 176, 161),
    "aero blue"                 : (201, 255, 229),
    "affair"                    : (113,  70, 147),
    "akaroa"                    : (212, 196, 168),
    "alabaster"                 : (250, 250, 250),
    "albescent white"           : (245, 233, 211),
    "algae green"               : (147, 223, 184),
    "alice blue"                : (240, 248, 255),
    "alizarin crimson"          : (227,  38,  54),
    "allports"                  : (  0, 118, 163),
    "almond"                    : (238, 217, 196),
    "almond frost"              : (144, 123, 113),
    "alpine"                    : (175, 143,  44),
    "alto"                      : (219, 219, 219),
    "aluminium"                 : (169, 172, 182),
    "amaranth"                  : (229,  43,  80),
    "amazon"                    : ( 59, 122,  87),
    "amber"                     : (255, 191,   0),
    "americano"                 : (135, 117, 110),
    "amethyst"                  : (153, 102, 204),
    "amethyst smoke"            : (163, 151, 180),
    "amour"                     : (249, 234, 243),
    "amulet"                    : (123, 159, 128),
    "anakiwa"                   : (157, 229, 255),
    "antique brass"             : (200, 138, 101),
    "antique bronze"            : (112,  74,   7),
    "anzac"                     : (224, 182,  70),
    "apache"                    : (223, 190, 111),
    "apple"                     : ( 79, 168,  61),
    "apple blossom"             : (175,  77,  67),
    "apple green"               : (226, 243, 236),
    "apricot"                   : (235, 147, 115),
    "apricot peach"             : (251, 206, 177),
    "apricot white"             : (255, 254, 236),
    "aqua deep"                 : (  1,  75,  67),
    "aqua forest"               : ( 95, 167, 119),
    "aqua haze"                 : (237, 245, 245)}
def build_reverse_dict():
    global reverse
    global colorhex
    global colors
    for color in colors:
        rgb = colors[color]
        hex_val = '#%02X%02X%02X' % (rgb)
        reverse[hex_val] = color
        colorhex[color] = hex_val
    return


def get_complementary_hex(color):
    # strip the # from the beginning
    color = color[1:]
    # convert the string into hex
    color = int(color, 16)
    # invert the three bytes
    # as good as substracting each of RGB component by 255(FF)
    comp_color = 0xFFFFFF ^ color
    # convert the color back to hex by prefixing a #
    comp_color = "#%06X" % comp_color
    # return the result
    return comp_color

def get_complementary_rgb(red, green, blue):
    color_string = '#%02X%02X%02X' % (red, green, blue)
    # strip the # from the beginning
    color = color_string[1:]
    # convert the string into hex
    color = int(color, 16)
    # invert the three bytes
    # as good as substracting each of RGB component by 255(FF)
    comp_color = 0xFFFFFF ^ color
    # convert the color back to hex by prefixing a #
    comp_color = "#%06X" % comp_color
    # return the result
    return comp_color

def get_name_from_hex(hex):
    global reverse
    global colorhex
    global colors

    hex_val = hex.upper()
    try:
        name = reverse[hex_val]
    except:
        name = 'No Hex For Name'
    return name

def get_hex_from_name(name):
    global reverse
    global colorhex
    global colors

    name = name.lower()
    try:
        hex_val = colorhex[name]
    except:
        hex_val = '#000000'
    return hex_val

def show_all_colors_on_buttons():
    global reverse
    global colorhex
    global colors
    window = sg.Window('Colors on Buttons Demo', default_element_size=(3, 1), location=(0, 0), font=("Helvetica", 7))
    row = []
    row_len = 20
    for i, c in enumerate(colors):
        hex_val = get_hex_from_name(c)
        button1 = sg.CButton(button_text=c, button_color=(get_complementary_hex(hex_val), hex_val), size=(8, 1))
        button2 = sg.CButton(button_text=c, button_color=(hex_val, get_complementary_hex(hex_val)), size=(8, 1))
        row.append(button1)
        row.append(button2)
        if (i+1) % row_len == 0:
            window.AddRow(*row)
            row = []
    if row != []:
        window.AddRow(*row)
    window.Show()


GoodColors = [('#0e6251', sg.RGB(255, 246, 122)),
              ('white', sg.RGB(0, 74, 60)),
              (sg.RGB(0, 210, 124), sg.RGB(0, 74, 60)),
              (sg.RGB(0, 210, 87), sg.RGB(0, 74, 60)),
              (sg.RGB(0, 164, 73), sg.RGB(0, 74, 60)),
              (sg.RGB(0, 74, 60), sg.RGB(0, 74, 60)),
              ]


def main():
    global colors
    global reverse

    build_reverse_dict()
    list_of_colors = [c for c in colors]
    printable = '\n'.join(map(str, list_of_colors))
    # show_all_colors_on_buttons()
    sg.set_options(element_padding=(0,0))
    while True:
        # -------  Form show  ------- #
        layout = [[sg.Text('Find color')],
                  [sg.Text('Demonstration of colors')],
                  [sg.Text('Enter a color name in text or hex #RRGGBB format')],
                  [sg.InputText(key='-HEX-')],
                  [sg.Listbox(list_of_colors, size=(20, 30), bind_return_key=True, key='-LISTBOX-'), sg.Text('Or choose from list')],
                  [sg.Submit(), sg.Button('Many buttons', button_color=('white', '#0e6251'), key='-MANY BUTTONS-'), sg.ColorChooserButton( 'Chooser', target=(3,0), key='-CHOOSER-'),  sg.Quit(),],
                  ]
                  # [g.Multiline(DefaultText=str(printable), Size=(30,20))]]
        event, values = sg.Window('Color Demo', layout, auto_size_buttons=False).read()

        # -------  OUTPUT results portion  ------- #
        if event == 'Quit' or event == sg.WIN_CLOSED:
            exit(0)
        elif event == '-MANY BUTTONS-':
                show_all_colors_on_buttons()

        drop_down_value = values['-LISTBOX-']
        hex_input = values['-HEX-']
        if hex_input == '' and len(drop_down_value) == 0:
            continue

        if len(hex_input) != 0:
            if hex_input[0] == '#':
                color_hex = hex_input.upper()
                color_name = get_name_from_hex(hex_input)
            else:
                color_name = hex_input
                color_hex = get_hex_from_name(color_name)
        elif drop_down_value is not None and len(drop_down_value) != 0:
            color_name = drop_down_value[0]
            color_hex  = get_hex_from_name(color_name)

        complementary_hex = get_complementary_hex(color_hex)
        complementary_color = get_name_from_hex(complementary_hex)

        layout = [[sg.Text('That color and it\'s compliment are shown on these buttons. This form auto-closes')],
                  [sg.CloseButton(button_text=color_name, button_color=(color_hex, complementary_hex))],
                  [sg.CloseButton(button_text=complementary_hex + ' ' + complementary_color, button_color=(complementary_hex , color_hex), size=(30, 1))],
                  ]
        sg.Window('Color demo', layout, default_element_size=(100, 1),
                        auto_close=True, auto_close_duration=5).read()



if __name__ == '__main__':
    main()