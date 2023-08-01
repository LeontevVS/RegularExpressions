import csv
import re


class ContactsFixer:
    
    def __init__(self, input_filename='phonebook_raw.csv', output_filename="phonebook.csv"):
        self._read_file(input_filename)
        self._fix_names()
        self._remove_duplicates()
        self._fix_phones()
        self._write_file(output_filename)

    def _read_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.contacts = list(reader)

    def _write_file(self, filename):
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            fieldnames = self.contacts[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.contacts)

    def _fix_names(self):
        for contact in self.contacts:
            name = f"{contact['lastname']} {contact['firstname']} {contact['surname']}"
            result = re.search(r'\s*(\w+)\s*(\w+)\s*(\w+)*\s*', name)
            contact['lastname'] = result.group(1)
            contact['firstname'] = result.group(2)
            contact['surname'] = '' if result.group(3) is None else result.group(3)

    def _remove_duplicates(self):
        def merge_contacts(contact1, contact2):
            merged_contact = {
                'email': contact1.get('email') if contact2.get('email') == '' else contact2.get('email'),
                'firstname': contact1.get('firstname') if contact2.get('firstname') == '' else contact2.get('firstname'),
                'lastname': contact1.get('lastname') if contact2.get('lastname') == '' else contact2.get('lastname'),
                'organization': contact1.get('organization') if contact2.get('organization') == '' else contact2.get('organization'),
                'phone': contact1.get('phone') if contact2.get('phone') == '' else contact2.get('phone'),
                'position': contact1.get('position') if contact2.get('position') == '' else contact2.get('position'),
                'surname': contact1.get('surname') if contact2.get('surname') == '' else contact2.get('surname')
            }
            return merged_contact
        clear_contacts = list()
        while len(self.contacts) != 0:
            contact = self.contacts.pop(0)
            duplicates_indexes = list()
            for index, check_contact in enumerate(self.contacts):
                if contact["firstname"] == check_contact["firstname"] and contact["lastname"] == check_contact["lastname"]:
                    contact = merge_contacts(contact, check_contact)
                    duplicates_indexes.append(index)
            self.contacts = [elem for index, elem in enumerate(self.contacts) if index not in duplicates_indexes]
            clear_contacts.append(contact)
        self.contacts = clear_contacts

    def _fix_phones(self):
        def get_repl(match_obj):
            if match_obj.group(7) is None:
                return f'+7({match_obj.group(2)}){match_obj.group(3)}-{match_obj.group(4)}-{match_obj.group(5)}'
            else:
                return f'+7({match_obj.group(2)}){match_obj.group(3)}-{match_obj.group(4)}-{match_obj.group(5)} доб.{match_obj.group(7)}'
        pattern = re.compile(r"(\+7|8)\s*\(*(\d\d\d)\)*[-\s]*(\d\d\d)[-\s]*(\d\d)[-\s]*(\d\d)\s*\(*(доб\.)*\s*(\d+)*\)*")   
        for contact in self.contacts:
            contact['phone'] = pattern.sub(get_repl, contact['phone'])