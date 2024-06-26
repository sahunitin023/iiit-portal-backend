class ReadOnlyInLine:

    can_delete = False
    
    def get_readonly_fields(self, request, obj=None):
        # Return all fields as read-only
        return [field.name for field in self.model._meta.fields]
