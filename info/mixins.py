class ReadOnlyInLine:

    can_delete = False
    
    def get_readonly_fields(self, request, obj=None):
        # Return all fields as read-only
        return [field.name for field in self.model._meta.fields if field.name!='class_id']

    # def has_add_permission(self, *args, **kwargs) -> bool:
    #     return False