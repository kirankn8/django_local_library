from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

# Create your models here.


class Genre(models.Model):
    """
    Model representing a book genre
    """

    name = models.CharField(max_length=200, help_text="Enter book genre")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.) 
        """

        return self.name


class Language(models.Model):
    """
    Model representing a Language (e.g. English, French, Japanese, etc.)
    """
    name = models.CharField(max_length=200,
                            help_text="Enter a the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Author(models.Model):
    """
    Models representing author
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True,blank=True)
    date_of_death = models.DateField('Died',null=True,blank=True)

    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance.
        :return: 
        """
        return reverse('catalog:author-detail',args=[str(self.id)])


    def __str__(self):
        """
        String represent the model object
        :return: 
        """
        return '%s, %s' % (self.last_name,self.first_name)


class Book(models.Model):
    """
    Model representing book
    """
    title = models.CharField(max_length=200)
    # author is foreign key
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    # imprint
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey(Language,on_delete=models.SET_NULL,null=True)

    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'


    def __str__(self):
        """
        String for representing the Model object
        :return title: 
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the url to access a particullar boook instance
        :return: 
        """
        return reverse('catalog:book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """
        Model representing a specific copy of a book (i.e. that can be borrowed from the library).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    imprint = models.DateField(null=True, blank=True)
    due_back = models.DateField(null=True, blank=True)

    # loan status is a tuple of tuples containing status
    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='d', help_text='Book availability')

    @property
    def is_overdue(self):
        if date.today() > self.due_back:
            return True
        return False

    class Meta:

        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """
        String representing model object
        :return: 
        """
        return '%s(%s)' % (self.id, self.book.title)
