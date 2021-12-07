from django import forms

class URLForm(forms.Form):
    url = forms.URLField(
        label="Website to index",
        help_text="Enter the web address to the website that you'd like to save",
    )

class QueryForm(forms.Form):
    query = forms.CharField(
        label="Query",
        help_text="Enter a query to search through previously indexed documents"
    )
