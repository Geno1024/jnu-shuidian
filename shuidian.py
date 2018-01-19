# Created by Geno1024 @ 2018-01-20 04:50

import base64
import binascii
import json
import requests
import sys
from Crypto.Cipher import AES
from datetime import datetime


# noinspection SpellCheckingInspection
def dec(string):
    return AES.new(
        b'CetSoftEEMSysWeb',
        AES.MODE_CBC,
        binascii.unhexlify('1934577290ABCDEF1264147890ACAE45')
    ).decrypt(base64.b64decode(string))


# noinspection SpellCheckingInspection
def enc(string):
    string += '\x10' * (16 - len(string) % 16)
    return base64.b64encode(
        AES.new(
            b'CetSoftEEMSysWeb',
            AES.MODE_CBC,
            binascii.unhexlify('1934577290ABCDEF1264147890ACAE45')
        ).encrypt(string)
    )


def _session():
    return requests.post(
        'http://10.136.2.5/JNUWeb/webservice/JNUService.asmx/GetEnergyTypeInfo',
        data=json.dumps({'nodeType': 0, 'nodeID': 0}),
        headers={'Referer': 'http://10.136.2.5/JNUWeb/', 'Content-Type': 'application/json'}
    ).cookies['ASP.NET_SessionId']


def _customer(room):
    return json.loads(
        requests.post(
            'http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/Login',
            data=json.dumps({'user': room, 'password': str(enc(''))}),
            headers={
                'Referer': 'http://10.136.2.5/JNUWeb/',
                'Content-Type': 'application/json',
                'Cookie': 'ASP.NET_SessionId=' + session
            },
        ).text
    )['d']['ResultList'][0]['customerId']


def _date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _info(room, api):
    uid = _customer(room)
    time = _date()
    cookie = 'ASP.NET_SessionId=' + session + '; jnu-lp=' + enc(room).decode('utf-8')
    token = enc('{\"userID\":' + str(uid) + ',\"tokenTime\":\"' + time + '\"}')
    return requests.post(
        'http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/' + api,
        headers={
            'Referer': 'http://10.136.2.5/JNUWeb/',
            'Content-Type': 'application/json; charset=UTF-8',
            'DateTime': str(time),
            'X-Requested-With': 'XMLHttpRequest',
            'Token': token,
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Cookie': cookie
        }
    ).text


def _info_with_data(room, api, data):
    uid = _customer(room)
    time = _date()
    cookie = 'ASP.NET_SessionId=' + session + '; jnu-lp=' + enc(room).decode('utf-8')
    token = enc('{\"userID\":' + str(uid) + ',\"tokenTime\":\"' + time + '\"}')
    return requests.post(
        'http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/' + api,
        headers={
            'Referer': 'http://10.136.2.5/JNUWeb/',
            'Content-Type': 'application/json; charset=UTF-8',
            'DateTime': str(time),
            'X-Requested-With': 'XMLHttpRequest',
            'Token': token,
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Cookie': cookie
        },
        data=data
    ).text


def get_account_balance(room):
    return json.loads(_info(room, 'GetAccountBalance'))['d']['balance']


def get_user_info(room):
    return json.loads(_info(room, 'GetUserInfo'))['d']['ResultList']


def get_bill_cost(room, start, end):
    return json.loads(
        _info_with_data(
            room,
            'GetBillCost',
            '{\"energyType\":0,\"startDate\":\"' + start + '\",\"endDate\":\"' + end + '\"}'
        )
    )['d']['ResultList']


def get_subsidy(room, start, end):
    return json.loads(
        _info_with_data(
            room,
            'GetSubsidy',
            '{\"startDate\":\"' + start + '\",\"endDate\":\"' + end + '\"}'
        )
    )['d']['ResultList']


def get_customer_metrical_data(room, start, end, interval):
    return json.loads(
        _info_with_data(
            room,
            'GetCustomerMetricalData',
            '{\"energyType\":0,\"startDate\":\"' + start + "\",\"endDate\":\"" + end + '\",\"interval\":' + str(
                interval) + '}'
        )
    )['d']['ResultList']


def get_payment_record(room, count, time):
    return json.loads(
        _info_with_data(
            room,
            'GetPaymentRecord?_dc=' + str(time),
            '{\"startIdx\":0,\"recordCount\":' + str(count) + '}'
        )
    )['d']['ResultList']


if __name__ == '__main__':
    room = sys.argv[1]
    session = _session()
    print(get_account_balance(room))
    print(get_user_info(room))
    print(get_bill_cost(room, '2017-12-01', '2018-01-01'))
    print(get_subsidy(room, '2017-12-01', '2018-01-01'))
    print(get_customer_metrical_data(room, '2017-12-01', '2018-01-01', 1))
    print(get_customer_metrical_data(room, '2017-01-01', '2018-01-01', 3))
    print(get_payment_record(room, 10, int(datetime.now().timestamp())))

