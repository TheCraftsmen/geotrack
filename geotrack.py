from flask.views import MethodView as MV
from flask.ext.via import Via
from flask.ext.via.routers.default import Pluggable as P
from flask import Flask, jsonify, render_template, request
import rethinkdb as r

app = Flask(__name__)
app.config['VIA_ROUTES_MODULE'] = 'geotrack'
app.config['VIA_ROUTES_NAME'] = 'routes'
conn = r.connect(host='localhost',
                 port=28015,
                 db='geotrack')

#r.db_create('geotrack').run(conn)
#r.db('geotrack').table_create('track').run(conn)


Geotrack = type('Geotrack', (MV,), {
		'get': lambda self, id=None: 
			jsonify({'data':[row for row in (r.table('track').filter({'id':id}).run(conn)\
			if id else \
			r.table('track').run(conn))]})
		,
		'post': lambda self, id=None: jsonify(**dict(r.table('track').\
				insert([{
    				'name': request.form['name'],
    				'location': r.point(float(request.form['a']),
    					                float(request.form['b']))
    				}])\
				.run(conn)))
		,
		'put': lambda self, id=None:
			r.table('track').get(id).\
			update([{
    				'location': r.point(request.form['a'],
    					                request.form['b'])
    				}]).run(conn) \
			if isinstance(id, int) else 404
		,
		'delete' : lambda self, id=None:
			r.table('track').get(id).delete().run(conn) \
			if isinstance(id, int) else 404
		,
	})


Index = type('Index', (MV,),{
	'get': lambda self: render_template('index.html')

	})

routes = [
    P('/geotrack/', Geotrack, 'geotrack'),
    P('/geotrack/<id>', Geotrack, 'geotrackid'),
    P('/',Index, 'index')
]


via = Via()
via.init_app(app)


if __name__ == '__main__':
	app.run(debug=True)



#---------------------------------------------------


"""
a, map(lambda x: [P('/geotrack/', Geotrack, 'geotrack'),
				  P('/geotrack/<id>', Geotrack, 'geotrackid')], [[type(),2]])
"""
