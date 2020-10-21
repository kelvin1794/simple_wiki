from django.db import connections
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import status


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class QueryView(APIView):
    """
    An endpoint that receives an arbitrary SQL query
    and returns the result ofexecuting the query on the database

    """

    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        """
        Check for SQL query sent with request body
        """
        cursor = connections["simplewiki"].cursor()
        query = request.data.get("query", "")
        if query == "":
            return Response(
                {"message": "Please include query in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            cursor.execute(query)
            data = dictfetchall(cursor)
            return Response(data)


class MostOutdatedPage(APIView):
    """
    Endpoint that receives a category
    and returns the ​mostoutdated​page for that category

    """

    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        """
        Only POST request is accepted
        Check for category sent with request body

        """

        cursor = connections["simplewiki"].cursor()
        query_placeholder = """
            select
                p.page_id, 
                p.page_namespace, 
                p.page_title, 
                p.page_touched, 
                cl.cl_to,
                pl.pl_namespace, 
                pl.pl_title, 
                pl.pl_from_namespace, 
                p2.page_touched as page_link_touched, 
                p2.page_touched - p.page_touched as outdatedness
            from page p
            inner join categorylinks cl on p.page_id = cl.cl_from and cl_to = %s
            inner join pagelinks pl on p.page_id = pl.pl_from
            inner join page p2 on pl.pl_namespace = p2.page_namespace and pl.pl_title = p2.page_title
            where p.page_touched < p2.page_touched
            ORDER BY outdatedness desc
            LIMIT 1;
        """

        category = request.data.get("category", "")
        cursor.execute(query_placeholder, [category])
        data = dictfetchall(cursor)

        return Response(data)