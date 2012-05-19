# -*- coding: utf-8 -*-

class EnumChoices(object):
    """Перечисление x, годное для использования в описании поля модели как choices=x.
    Аргументы для создания: символьное обозначение константы, текстовая константа для форм
    В базу будут записаны числовые значения, автоматически расставленные классом. В формах будут
    отображаться текстовые константы, которые полезно окружать gettext-ом.

    Например:
        status = EnumChoices(on=_("Published"), off=("Hidden"))
        создаёт перечисление status, которое можно передать в IntegerField(choices=status).
        Для использования во вьюхах доступны аттрибуты
            status.on == 0
            status.off == 1

    Для пущей шоколадности, перечисление следует создавать в scope модели, его использующей.
    Например:
        class Account(models.Model):
            Status = EnumChoices(
                unapproved=_("Awaiting approve"),
                active=_("Active"),
                suspended=_("Inactive"),
                deleted=_("Deleted"),
            )
            user = models.ForeignKey(User)
            status = models.IntegerField(choices=Status, default=Status.unapproved)
            balance = models.IntegerField()
            comment = models.TextField()
        ...
        a = Account(user=request.user, balance=100, comment='new user')
        active_accounts = Account.objects.filter(status=Account.Status.active)
    """

    def __init__(self, **kwargs):
        self.attrs = []
        self.key_hash = dict()
        if kwargs['ordering']:
            index = 0
            for key in kwargs['ordering']:
                self.attrs.append((index, kwargs[key]))
                setattr(self, key, index)
                self.key_hash[key] = index
                index += 1
        else:
            index = 0
            for key, value in kwargs.iteritems():
                self.attrs.append( (index, value) )
                setattr(self, key, index)
                self.key_hash[key] = index
                index += 1

    def __iter__(self):
        return self.attrs.__iter__()

    def __getitem__(self, index):
        return self.attrs[index][1]

    def __len__(self):
        return len(self.attrs)

    def key2index(self, key):
        try:
            return self.key_hash[key]
        except KeyError:
            return None

    def index2key(self, index):
        try:
            return self.key_hash.keys()[self.key_hash.values().index(index)]
        except ValueError:
            return None
