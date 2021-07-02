import re
from flask import Flask, render_template
from .constants import CODE_REG, PRODUCT_TYPE

app = Flask(__name__)


def read_package_codes():
    codes = []
    with open('app/database', 'r') as fl:
        for line in fl.readlines():
            code = line.split(': ')[1] # get package code
            codes.append(code)
        return codes


def check_product_type(product_type):
    if product_type not in PRODUCT_TYPE.keys():
        return 'O produto não possui um tipo válido.'


def check_send_package(cod_origin, cod_type, origin=('111',), product_type=('000',)):
    if (cod_origin in origin) and (cod_type in product_type):
        return 'Não é possível despachar pacotes contendo jóias tendo como região de origem o Centro-oeste.'


def check_code_seller(cod_seller, check_cod_seller=('584',)):
    if cod_seller in check_cod_seller:
        return 'O vendedor está com seu CNPJ inativo e, portanto, não pode mais enviar pacotes pela Loggi.'


def check_destino(cod_destino):
    return CODE_REG[cod_destino]


def check_destino_type(cod_destino, cod_type, destinos=('000',), types=('888',)):
    if (cod_destino in destinos) and (cod_type in types):
        return True 


def code_destino_type(package_codes):
    code_dict = {}
    for code, dict  in package_codes.items():
        compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        splited_code = compiler.search(code)
        result = check_destino_type(
            splited_code.group(2),
            splited_code.group(5)
        )
        destino = check_destino(splited_code.group(2))
        if result is not None:
            code_dict[code] = {'status':dict['status'], 'destino':destino}
    return code_dict


def code_destino_group(package_codes):
    dest_dict = {}
    for code, dict  in package_codes.items():
        if dict['status'] == 'Válido':
            if dict['destino'] not in dest_dict.keys():
                dest_dict[dict['destino']] = []
            dest_dict[dict['destino']].append(code)
    return dest_dict


def code_destino(package_codes):
    code_dict = {}
    for code, dict  in package_codes.items():
        compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        splited_code = compiler.search(code)
        destino = check_destino(splited_code.group(2))
        code_dict[code] = {'status':dict['status'], 'destino':destino}
    return code_dict


def split_package_code_to_verify():
    dict_codes = {}
    package_codes = read_package_codes()
    for code in package_codes:
        compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        splited_code = compiler.search(code)

        result_product_type = check_product_type(splited_code.group(5))
        result_code_seller = check_code_seller(splited_code.group(4))
        result_send_package = check_send_package(
            splited_code.group(1),
            splited_code.group(5)
        )
        
        if result_product_type is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_product_type}
        elif result_send_package is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_send_package}
        elif result_code_seller is not None:
            dict_codes[code] = {'status':'Inválido', 'observation': result_code_seller}
        else:
            dict_codes[code] = {'status':'Válido', 'observation': None}
    return dict_codes


def code_seller_origin(package_codes):
    code_dict = {}
    for code, value  in package_codes.items():
        if value['status'] == 'Válido':
            compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
            splited_code = compiler.search(code)
            key = splited_code.group(4)
            if key not in code_dict.keys():
                code_dict[key] = ([], CODE_REG[splited_code.group(2)])
            code_dict[key][0].append(code)
    for key in code_dict.keys():
        code_dict[key] = {'vendas': len(code_dict[key][0])}
    return code_dict


def code_type_group(package_codes):
    dest_dict = {}
    for code, dict  in package_codes.items():
        compiler = re.compile('(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})')
        splited_code = compiler.search(code)
        if dict['status'] == 'Válido' and splited_code.group(5) in PRODUCT_TYPE and splited_code.group(2) in CODE_REG:
            type_product = PRODUCT_TYPE[splited_code.group(5)]
            destino = CODE_REG[splited_code.group(2)]
            if type_product not in dest_dict.keys():
                dest_dict[type_product] = []
            dest_dict[type_product].append((code, destino))
    return dest_dict


@app.route("/")
def valid_codes(codes=None):
    package_codes = split_package_code_to_verify()
    return render_template('valid_codes.html', codes=package_codes)


@app.route("/destino")
def destino():
    package_codes = split_package_code_to_verify()
    codes = code_destino(package_codes)
    return render_template('destinos.html', codes=codes)


@app.route("/brinquedos-sul")
def brinquedos_sul():
    package_codes = split_package_code_to_verify()
    codes = code_destino_type(package_codes)
    return render_template('brinquedos_sul.html', codes=codes)


@app.route("/grupo-regiao")
def grupo_regiao():
    package_codes = split_package_code_to_verify()
    codes = code_destino(package_codes)
    codes = code_destino_group(codes)
    return render_template('grupo_regiao.html', codes=codes)


@app.route("/vendas-por-vendedor")
def vendas_por_vendedor():
    codes = split_package_code_to_verify()
    codes = code_seller_origin(codes)
    return render_template('vendas_por_vendedor.html', codes=codes)


@app.route("/destino-e-tipo")
def destino_e_tipo():
    package_codes = split_package_code_to_verify()
    codes = code_type_group(package_codes)
    return render_template('tipo.html', codes=codes)