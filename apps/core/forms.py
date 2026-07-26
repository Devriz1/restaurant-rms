from django import forms


class BaseModelForm(forms.ModelForm):

    """
    Common form styling for RMS
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            widget = field.widget

            current_class = widget.attrs.get(
                "class",
                ""
            )

            if isinstance(
                widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                    forms.NumberInput,
                    forms.PasswordInput,
                    forms.DateInput,
                    forms.TimeInput,
                    forms.Select,
                    forms.Textarea,
                ),
            ):

                widget.attrs["class"] = (
                    current_class
                    + " form-control"
                ).strip()