#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime as datetime
import re
from slugify import slugify


class Person(object):
    def __init__(self, name, address, registrationNumber, memberFrom, born, honors):
        self.honors = honors
        self.born = born
        self.memberFrom = memberFrom
        self.registrationNumber = registrationNumber
        self.address = address
        self.name = name


class Honor(object):
    def __init__(self, year, type, text):
        self.year = year
        self.type = type
        self.text = text


lines = [line.rstrip('\n') for line in open('firemans.txt')]

persons = []
beginOfPersonCounter = 0
counter = 0
for line in lines:
    if line == '=====================================================':
        beginOfPersonCounter = counter - 1

    if line == '' and lines[counter + 1] == '':
        name = lines[beginOfPersonCounter]
        street = lines[beginOfPersonCounter + 2].strip('Adresa: ')
        if street != '':
            street = street + ', '
        address = street + lines[beginOfPersonCounter + 3].strip('Město: ')
        registrationNumber = lines[beginOfPersonCounter + 5].strip('Registrační číslo: ').split(' ', 1)[0]
        datePattern = '[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]'
        memberFrom = re.findall(datePattern, lines[beginOfPersonCounter + 5])[0] ### 1989-12-30 00:00:00
        born = re.findall(datePattern, lines[beginOfPersonCounter + 6])[0]
        honorsCount = counter - (beginOfPersonCounter + 8)
        honors = []
        if honorsCount > 0:
            beginOfHonors = beginOfPersonCounter + 8
            endOfHonors = counter
            for i in range(beginOfHonors, endOfHonors):
                years = re.findall('[0-9][0-9][0-9][0-9]', lines[i].strip('- '))
                text = lines[i].split(': ', 1)[1]
                typeNormalized = slugify(text.decode('utf-8'))
                for year in years:
                    honor = Honor(year, typeNormalized, text)
                    honors.append(honor)
        person = Person(name, address, registrationNumber, memberFrom, born, honors)
        persons.append(person)

    counter = counter + 1

for person in persons:
    url = slugify(person.name.decode('utf-8')).strip()
    print 'INSERT INTO hs_firemans (`name`, `born`, `firemansince`, `address`, `url`) VALUES (\'' + person.name + '\',STR_TO_DATE(\'' + person.born + '\', \'%d.%m.%Y\'), STR_TO_DATE(\'' + person.memberFrom + '\', \'%d.%m.%Y\'), \'' + person.address + '\',\'' + url.encode('utf-8') + '\')' \
            ' ON DUPLICATE KEY UPDATE born = STR_TO_DATE(\'' + person.born + '\', \'%d.%m.%Y\'), firemansince = STR_TO_DATE(\'' + person.memberFrom + '\', \'%d.%m.%Y\'), address = \'' + person.address + '\';'
    for honor in person.honors:
        select = '(SELECT id FROM hs_firemans WHERE name = \'' + person.name + '\')'
        print 'INSERT INTO hs_firemans_honors (year, type, text, fireman_id) VALUES (\'' + honor.year + '\',\'' + honor.type.encode('utf-8') + '\',\'' + honor.text + '\', ' + select + ');'

