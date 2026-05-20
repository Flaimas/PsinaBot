def sub_template(username: str):
    STANDART = {
    'username': username,
    'data_limit': 214748364800,
    'expire': 2592000,
    'note': 'STANDART',
    'data_limit_reset_strategy0': 'month',
    'status': 'on_hold',
    'inbounds': {
        'vless':[
            'VLESS TCP REALITY',
            'VLESS TCP TLS'
        ]
    },
    'proxies': {
        'vless': {
            'flow': 'xtls-rprx-vision'
        }
    }
    }