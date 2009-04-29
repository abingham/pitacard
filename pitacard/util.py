def link_widgets(xml, obj, names):
    '''
    links widgets from a glade XML file to attributes
    in an object. 'names' should be a list of names where
    each name is either a string or a tuple of the form
    (xml_name, attr_name).

    In both cases, a widget is looked up in the XML and
    bound via setattr as an attribute of the object. If
    name is a string, it is used for both the lookup and
    the attribute name. If it's a tuple, the first element
    is used for the lookup and the second name is used for
    the attribute.
    '''
    for name in names:
        if type(name) is str:
            setattr(obj, name, xml.get_widget(name))
        elif type(name) is tuple and len(name) >= 2:
            setattr(obj, name[1], xml.get_widget(name[0]))
        else:
            raise KeyError

def get_text(text_view):
    return text_view.get_buffer().get_text(*text_view.get_buffer().get_bounds())
