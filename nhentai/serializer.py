# coding: utf-8


def serialize(doujinshi):
    metadata = {'Title'    : doujinshi.name,
                'Subtitle' : doujinshi.info.subtitle}
    if doujinshi.info.date:
        metadata['Upload_Date'] = doujinshi.info.date
    if doujinshi.info.parodies:
        metadata['Parodies']    = [i.strip() for i in doujinshi.info.parodies.split(',')]
    if doujinshi.info.characters:
        metadata['Characters']  = [i.strip() for i in doujinshi.info.characters.split(',')]
    if doujinshi.info.tags:
        metadata['Tags']        = [i.strip() for i in doujinshi.info.tags.split(',')]
    if doujinshi.info.artists:
        metadata['Artists']     = [i.strip() for i in doujinshi.info.artists.split(',')]
    if doujinshi.info.groups:
        metadata['Groups']      = [i.strip() for i in doujinshi.info.groups.split(',')]
    if doujinshi.info.languages:
        metadata['Languages']   = [i.strip() for i in doujinshi.info.languages.split(',')]
    metadata['Categories']      = doujinshi.info.categories
    metadata['URL']             = doujinshi.url
    metadata['Pages']           = doujinshi.pages
    return metadata
