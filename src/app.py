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
    if int(product_type) not in PRODUCT_TYPE.keys():
        return 'O produto não possui possui um tipo válido.'


def check_send_package(cod_origin, cod_type, origin=111, product_type=000):
    if (int(cod_origin) == origin) and (int(cod_type) == product_type):
        print('Não é possível despachar pacotes contendo jóias tendo como região de origem o Centro-oeste.')
        return 'Não é possível despachar pacotes contendo jóias tendo como região de origem o Centro-oeste.'


def check_code_seller(cod_seller, check_cod_seller=(584,)):
    if int(cod_seller) in check_cod_seller:
        return 'O vendedor está com seu CNPJ inativo e, portanto, não pode mais enviar pacotes pela Loggi.'


def split_package_code_to_verify():
    dict_codes = {}
    package_codes = read_package_codes()
    for code in package_codes:
        compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        splited_code = compiler.search(code)

        result_product_type = check_product_type(splited_code.group(5))
        result_send_package = check_send_package(splited_code.group(1), splited_code.group(5))
        result_code_seller = check_code_seller(splited_code.group(4))

        if result_product_type is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_product_type}
        elif result_send_package is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_send_package}
        elif result_code_seller is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_code_seller}
        else:
            dict_codes[code] = {'status':'Válido', 'observation': None}
    return dict_codes


@app.route("/")
def valid_codes(codes=None):
    package_codes = split_package_code_to_verify()
    return render_template('valid_codes.html', codes=package_codes)


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)