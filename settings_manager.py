import base64


def decode_string(string_to_decode):
    data = base64.b64decode(string_to_decode).decode('utf8')
    return data


def encode_string(string_to_encode):
    data = base64.b64encode(string_to_encode)
    return data


def read_settings_from_file(file_name='user_settings_test.txt'):
    data = ""
    with open(file_name, 'r') as file:
        data = decode_string(file.read()).replace("\r", "").replace("\n", "")

    return data


def write_data_to_file(settings_string, file_name='user_settings_test.txt'):
    data = encode_string(settings_string)
    with open(file_name, 'wb') as file:
        file.write(data)


""" #Пример использования:
encoded = encode_string(b'data to be encoded')
print(encoded)
data = decode_string (encoded)
print(data)
write_data_to_file(b'data to be encoded')
print(read_settings_from_file())
////////////////////////////////

Формат XML-файла с настройками:
<settings>
 <user>
  <estaff_username>yashin</estaff_username>
  <hh_username>aaa@mail.ru</hh_username>
  <hh_password>12345</hh_password>
  <chrome_options>
   <option>--profile-directory=Default</option>
   <option>--disable-plugins-discovery</option>
   <option>--ignore-certificate-errors</option>
   <option>user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64)
    AppleWebKit/537.36 (KHTML, like Gecko)
    Chrome/77.0.3865.90 Safari/537.36</option>
  </chrome_options>
 </user>
</settings> """
