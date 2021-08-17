from typing import Any, Dict, List, Tuple, Type
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from rest_framework.exceptions import NotFound


class IServiceBase:
    model: Type[Model] = None
    basequeryset: Type[QuerySet] = None


class IServiceRead(IServiceBase):
    paginator_class: Type[Paginator] = Paginator
    page_size: Type[int] = 10
    NOT_FOUND_MESSAGE: Type[str] = 'Not Found'

    def fetch(self, page=None, **filters) -> QuerySet:
        ''' Returns queryset of filtered objects '''
        query = self.basequeryset.filter(**filters).all()

        if page:
            paginator = self.paginator_class(query, self.page_size)
            return paginator.get_page(page)
        return query
        
    def retrieve(self, pk: Any) -> Model:
        ''' Return specific objects by pk '''
        try:
            return self.basequeryset.get(pk=pk)
        except self.model.DoesNotExist:
            raise NotFound(self.NOT_FOUND_MESSAGE)
    

class IServiceAction(IServiceBase):
    def validate_delete(self, **data) -> bool:
        return True

    def validate_update(self, **data) -> bool:
        return True

    def create(self, **data) -> Model:
        ''' Create new object '''
        new_obj = self.model(**data)
        new_obj.save()
        
        return new_obj
    
    def update(self, update_data: Dict, **filters) -> QuerySet:
        ''' Update type of objects '''
        objects = self.fetch(**filters).all()
        objects.update(**update_data)

        objects = self.fetch(**update_data).all()
        return objects
    
    def delete(self, **filters) -> Tuple[int, Dict[str, int]]:
        ''' Deletes type of objects '''
        self.validate_delete(**filters)

        delete_objects = self.basequeryset.filter(**filters).all()

        if len(delete_objects) == 0:
            raise ValidationError('Nothing to delete!')

        return delete_objects.delete()

    def bulk_delete(self, *pks) -> List[Any]:
        ''' Delete multiple objects '''
        deleted = []
        for pk in pks:
            try:
                deleted.append(
                    self.basequeryset.get(pk=pk).delete()
                )
            except self.model.DoesNotExist:
                continue
        return deleted


class IService(IServiceAction, IServiceRead):
    ''' 
        все действия с бд должны производиться только через наследников данного класса
        нельзя вызывать методы менеджера .delete, .create, .update и т.д. вне
        его наследников! 
    '''
    pass