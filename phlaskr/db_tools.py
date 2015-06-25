print_tables =\
        lambda\
            BaseModel:\
                ''.join(
                        map(
                        lambda x:\
                            '\n{}\n{}\n'.format(
                                                    x[0],
                                                    x[1].__table__.c.keys()
                                                ),filter(
                        lambda x: not x[0].startswith('_'),
                        BaseModel._decl_class_registry.items()
                    )
                )
            )

from models import BaseModel

print print_tables(BaseModel)
