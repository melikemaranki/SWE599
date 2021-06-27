from django import forms
from semantics.tasks import get_country_names, get_section_names
from django.db import models

Country_Choices= get_country_names()
Section_Choices = get_section_names()
Search_Choices=[('article title','article title'),
         ('article text','aricle text')]
class Search(models.Model):
	keyword = models.CharField(max_length=200, verbose_name="Search in Articles",blank= True)
	search = models.CharField(max_length=200,verbose_name = "",choices=Search_Choices, default = "article title",
	help_text="The keyword written above will be searched in the article text or title depending on your selection.")
	country = models.CharField(max_length=200,choices=Country_Choices, blank= True,
	help_text="Add a country to your search.")
	section = models.CharField(max_length=200,choices=Section_Choices, blank= True,
	help_text="Add a section to your search.")

	def __str__(self):
		return self.keyword + ' ' + self.country