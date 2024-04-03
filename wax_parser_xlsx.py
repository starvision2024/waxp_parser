import requests
import openpyxl
from itertools import cycle

file_in = 'e:\\max_wax.txt'          # Путь к файлу *.txt, в котором расположены названия кошельков, каждый с новой строки wallet.wam
file_out = 'e:\\max_results.xlsx'     # Путь к файлу, куда будут сохраняться результаты (Кошелек, Баланс Wax, Застейкано в CPU, NET, Запрошенный вывод)

# Функция для очистки строки от лишних символов и преобразования в число
def clean_and_convert_to_float(value_str):
    cleaned_str = ''.join(filter(lambda x: x.isdigit() or x == '.', value_str))
    return round(float(cleaned_str), 2) if cleaned_str else 0.0

def process_wallet(wallet_line, url, headers, results_sheet, processed_wallets):
    if wallet_line in processed_wallets:
        return

    data = f'{{"account_name":"{wallet_line}"}}'
    try:
        response_wax = requests.post(url, headers=headers, data=data).json()

        # Извлекаем значения
        core_liquid_balance_str = response_wax.get('core_liquid_balance', 'N/A')
        total_resources = response_wax.get('total_resources')
        net_weight_str = total_resources.get('net_weight', 'N/A') if total_resources else 'N/A'
        cpu_weight_str = total_resources.get('cpu_weight', 'N/A') if total_resources else 'N/A'
        refund_request = response_wax.get('refund_request', {})
        refund_request_str = refund_request.get('cpu_amount', 'N/A') if refund_request else 'N/A'

        core_liquid_balance = clean_and_convert_to_float(core_liquid_balance_str)
        net_weight = clean_and_convert_to_float(net_weight_str)
        cpu_weight = clean_and_convert_to_float(cpu_weight_str)
        refund_request = clean_and_convert_to_float(refund_request_str)

        # Записываем результаты в файл Excel
        row = [wallet_line, core_liquid_balance, cpu_weight, net_weight, refund_request]
        results_sheet.append(row)

        # Помечаем кошелек как обработанный
        processed_wallets.add(wallet_line)

    except IndexError:
        print(f"Ошибка индекса при обработке {wallet_line}. Пропускаем.")
    except Exception as e:
        print(f"Произошла ошибка при обработке {wallet_line}: {e}")

def main():
    with open(file_in, 'r') as file:
        wallet = [line.strip() for line in file]

    # Перебирайте адреса URL по очереди
    urls = [
        'https://api.wax.bountyblok.io/v1/chain/get_account',
        'https://api.waxsweden.org/v1/chain/get_account',
        # Добавьте другие URL-адреса, если необходимо
    ]

    headers = {
        'authority': 'wax.eosphere.io',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://waxblock.io',
        'referer': 'https://waxblock.io/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    # Создаем новый файл Excel
    workbook = openpyxl.Workbook()
    results_sheet = workbook.active
    results_sheet.append(['Wallet', 'Balance', 'CPU', 'NET', 'Refund'])

    # Словарь для отслеживания обработанных кошельков
    processed_wallets = set()

    # Итератор по списку URL, который будет циклически повторять URL
    url_iterator = cycle(urls)

    # Обрабатываем кошельки
    for wallet_line in wallet:
        # Берем следующий URL из цикла
        current_url = next(url_iterator)
        process_wallet(wallet_line, current_url, headers, results_sheet, processed_wallets)

    # Сохраняем файл Excel
    workbook.save(file_out)
    print(f"Обработка завершена. Результаты сохранены в файле '{file_out}'.")

if __name__ == "__main__":
    main()
