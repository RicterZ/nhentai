# coding: utf-8
import json
import os


def serialize(doujinshi, dir):
    metadata = {'title': doujinshi.name,
                'subtitle': doujinshi.info.subtitle}
    if doujinshi.info.date:
        metadata['upload_date'] = doujinshi.info.date
    if doujinshi.info.parodies:
        metadata['parody'] = [i.strip() for i in doujinshi.info.parodies.split(',')]
    if doujinshi.info.characters:
        metadata['character'] = [i.strip() for i in doujinshi.info.characters.split(',')]
    if doujinshi.info.tags:
        metadata['tag'] = [i.strip() for i in doujinshi.info.tags.split(',')]
    if doujinshi.info.artists:
        metadata['artist'] = [i.strip() for i in doujinshi.info.artists.split(',')]
    if doujinshi.info.groups:
        metadata['group'] = [i.strip() for i in doujinshi.info.groups.split(',')]
    if doujinshi.info.languages:
        metadata['language'] = [i.strip() for i in doujinshi.info.languages.split(',')]
    metadata['category'] = doujinshi.info.categories
    metadata['URL'] = doujinshi.url
    metadata['Pages'] = doujinshi.pages

    with open(os.path.join(dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, separators=','':')


def merge_json():
    lst = []
    output_dir = "./"
    os.chdir(output_dir)
    doujinshi_dirs = next(os.walk('.'))[1]
    for folder in doujinshi_dirs:
        files = os.listdir(folder)
        if 'metadata.json' not in files:
            continue
        data_folder = output_dir + folder + '/' + 'metadata.json'
        json_file = open(data_folder, 'r')
        json_dict = json.load(json_file)
        json_dict['Folder'] = folder
        lst.append(json_dict)
    return lst


def serialize_unique(lst):
    dictionary = {}
    parody = []
    character = []
    tag = []
    artist = []
    group = []
    for dic in lst:
        if 'parody' in dic:
            parody.extend([i for i in dic['parody']])
        if 'character' in dic:
            character.extend([i for i in dic['character']])
        if 'tag' in dic:
            tag.extend([i for i in dic['tag']])
        if 'artist' in dic:
            artist.extend([i for i in dic['artist']])
        if 'group' in dic:
            group.extend([i for i in dic['group']])
    dictionary['parody'] = list(set(parody))
    dictionary['character'] = list(set(character))
    dictionary['tag'] = list(set(tag))
    dictionary['artist'] = list(set(artist))
    dictionary['group'] = list(set(group))
    return dictionary


def set_js_database():
    with open('data.js', 'w') as f:
        indexed_json = merge_json()
        unique_json = json.dumps(serialize_unique(indexed_json), separators=','':')
        indexed_json = json.dumps(indexed_json, separators=','':')
        f.write('var data = ' + indexed_json)
        f.write(';\nvar tags = ' + unique_json)
