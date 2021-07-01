import re
from flask import Flask, render_template
from definitions import CODE_REG, PRODUCT_TYPE

app = Flask(__name__)


def read_package_codes():
    codes = []
    with open('database', 'r') as fl:
        for line in fl.readlines():
            code = line.split(': ')[1] # get package code
            codes.append(code)
        return codes


def check_product_type(product_type):
    if product_type not in PRODUCT_TYPE.keys():
        return 'O produto não possui possui um tipo válido'


def check_send_package(cod_origin, cod_type, origin=111, product_type=000):
    if cod_origin == origin and cod_type == product_type:
        return 'Não é possível despachar pacotes contendo jóias tendo como região de origem o Centro-oeste'


def check_code_seller(cod_seller, check_cod_seller=(584)):
    if cod_seller in check_cod_seller:
        return 'O vendedor está com seu CNPJ inativo e, portanto, não pode mais enviar pacotes pela Loggi,'


def split_package_code_to_verify():
    dict_codes = {}
    package_codes = read_package_codes()
    for code in package_codes:
        # dict_codes[code] = 
        c = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        f = c.search(code)

        if check_product_type(f.group(5)) and \
            check_send_package(f.group(1), f.group(5)) and \
            check_code_seller(f.group(4)):
            


@app.route("/")
def valid_codes(codes=None):
    
    return render_template('valid_codes.html', codes=package_codes)


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)