class BaseRepository:
    dto_model = None

    def to_dto(self, orm_obj):
        return self.dto_model.model_validate(orm_obj) # type: ignore

    def to_dto_list(self, orm_list):
        return [self.to_dto(o) for o in orm_list]
