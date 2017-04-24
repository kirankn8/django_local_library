from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.contrib.auth.decorators import permission_required
from .forms import RenewBookForm
from django.forms import ModelForm
# Create your views here.

from .models import Book, Author, BookInstance, Genre, Language


def index(request):
    """
    View function for home page of site
    :param request: 
    :return render: 
    """
    # Generate counts of some main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status ='a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    booklike = Book.objects.filter(title__icontains='aavaran').count()
    
    # Number of visits to this view,as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'booklikeavaran': booklike,
            'num_visits': num_visits,
        }
    )


class BookListView(LoginRequiredMixin,generic.ListView):
    model = Book
    # context_object_name = 'my_book_list'
    queryset = Book.objects.filter(title__icontains='a')[:5]
    template_name = 'book_list.html'
    paginate_by = 2
    '''
    def get_queryset(self):
        return Book.objects.filter(title__icontains='a')[:5]


    
    # First get the existing context from our superclass.
    # Then add your new context information.
    # Then return the new (updated) context.

    def get_context_data(self, **kwargs):
        context = super(BookListView,self).get_context_data()
        context[''] = 'This os just some data'
        return context
    '''


class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model = Book
    template_name = 'book_detail.html'


class AuthorListView(LoginRequiredMixin,generic.ListView):
    model = Author
    template_name = 'author_list.html'
    paginate_by = 3


class AuthorDetailView(LoginRequiredMixin,generic.DetailView):
    model = Author
    template_name = 'author_detail.html'


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('catalog:index'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })

    return render(request, 'book_renew_librarian.html', {'form': form, 'bookinst': book_inst})



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('catalog:authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class BookUpdate(UpdateView):
    model = Book
    fields = fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('catalog:books')