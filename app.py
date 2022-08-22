import os
import secrets
import traceback

from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from helpers import exceptionAsAJson, successAsJson, getDateTimeInMillis

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
api = Api(app)
# database
app.config["SECRET_KEY"] = '9bbd8f44c4ec734042fd241973766449'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///App.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['UPLOAD_FOLDER'] = "files/"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)
# init bcrypt
bcrypt = Bcrypt(app)


class Courthouse(db.Model):
    __tablename__ = 'courthouse'
    id = db.Column(db.Integer, primary_key=True)
    court_type = db.Column(db.String, nullable=False)
    court_location = db.Column(db.String, nullable=False)
    users = db.relationship('User', backref='Courthouse')
    number_of_cases_per_day = db.Column(db.Integer, nullable=False, default=5)
    fixed_case_dates = db.relationship('FixedCaseDate', backref='Courthouse')

    def __repr__(self):
        return self.id


class CourthouseSchema(ma.Schema):
    class Meta:
        fields = ('id', 'courttype', 'courtLocation')


# init schema
courthouse_schema = CourthouseSchema()
courthouses_schema = CourthouseSchema(many=True)


class CourthouseController(Resource):
    def get(self):
        court = Courthouse.query.all()
        return courthouses_schema.jsonify(court)

    def post(self):
        court_type = request.form.get('courtType')
        court_location = request.form.get('courtLocation')
        court = Courthouse(courtType=court_type, courtLocation=court_location)
        db.session.add(court)
        db.session.commit()
        return courthouse_schema.jsonify(court)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    city_of_origin = db.Column(db.String, nullable=False)
    court_house = db.Column(db.Integer, db.ForeignKey(
        'Courthouse.id'), nullable=False)
    role = db.Column(db.String, nullable=False)
    cases = db.relationship('Case', backref='User')
    fixed_case_dates = db.relationship('FixedCaseDate', backref='User')

    def __repr__(self):
        return str(self.id)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'fullname', 'city of origin', 'role')


# init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserController(Resource):
    def get(self):
        try:
            user = User.query.all()
            return users_schema.jsonify(user)
        except Exception as e:
            print(e)
            return exceptionAsAJson("user get", e)

    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        fullName = request.form.get('fullName')
        cityOfOrigin = request.form.get('cityOfOrigin')
        try:
            courtHouse = Courthouse.query.filter(
                Courthouse.id == request.form.get('courtHouse')).one()
            # print(courtHouse)courtHouseser post courthouse get", e)
        except Exception as e:
            print(e)
            return exceptionAsAJson("user post", str(e))
        role = request.form.get('role')
        user = User(username=username, password=password, fullName=fullName,
                    cityOfOrigin=cityOfOrigin, courtHouse=courtHouse.id, role=role)
        db.session.add(user)
        db.session.commit()
        return courthouse_schema.jsonify(user)


class GenericUserController(Resource):
    def get(self, userid):
        user = User.query.filter_by(id=userid).all()
        if user == None:
            return exceptionAsAJson("users get", "No user found")
        return users_schema.jsonify(user)

    def delete(self, userid):
        user = User.query.filter_by(id=userid).one()
        db.seesion.delete(user)
        db.session.commit()
        return successAsJson()

    def put(self, userid):
        user = User.query.filter_by(id=userid).all()
        user.username = request.json['username']
        user.password = request.json['password']
        user.fullName = request.json['fullName']
        user.cityOfOrigin = request.json['cityOfOrigin']
        user.courtHouse = request.json['courtHouse']
        user.role = request.json['role']
        user.cases = request.json['cases']
        user.fixedCaseDates = request.json['fixedCaseDates']
        db.session.commit()


class RequestHandler(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    request_type = db.Column(db.String, nullable=False)
    request_data = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    created_on = db.Column(
        db.String, default=getDateTimeInMillis(), nullable=False)

    def __repr__(self):
        return str(self.id)


class RequestHandlerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'fromuser', 'touser', 'requesttype',
                  'requestdata', 'status', 'createdon')


# init schema
request_schema = RequestHandlerSchema()
requests_schema = RequestHandlerSchema(many=True)


class RequestController(Resource):
    def get(self):
        requests = RequestHandler.query.all()
        return requests_schema.jsonify(requests)

    def post(self):
        fromUser = request.form.get('fromUser')
        toUser = request.form.get('toUser')
        requestType = request.form.get('requestType')
        requestData = request.form.get('requestData')
        status = request.form.get('status')
        request_handler = RequestHandler(fromUser=fromUser, toUser=toUser,
                                         requestType=requestType, requestData=requestData, status=status)
        db.session.add(request_handler)
        db.session.commit()


class GenericRequestController(Resource):
    def get(self, reqid):
        requests = RequestHandler.query.filter_by(id=reqid).all()
        return request_schema.jsonify(requests)

    def delete(self, reqid):
        requests = RequestHandler.query.filter_by(id=reqid).all()
        db.seesion.delete(requests)
        db.session.commit()

    def put(self, reqid):
        requests = RequestHandler.query.filter_by(id=reqid).all()
        requests.fromUser = request.json['fromUser']
        requests.toUser = request.json['toUser']
        requests.requestType = request.json['requestType']
        requests.requestData = request.json['requestData']
        requests.status = request.json['status']
        db.session.commit()


class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    assigned_advocate = db.Column(db.String, nullable=False)
    affidavit = db.Column(db.String, nullable=False)
    charge_sheet = db.Column(db.String, nullable=False)
    case_created_time = db.Column(
        db.String, default=getDateTimeInMillis(), nullable=False)
    last_modified = db.Column(
        db.String, default=getDateTimeInMillis(), nullable=False)
    case_status = db.Column(db.String, nullable=False, default="Not yet assigned")
    severity_index = db.Column(db.String, nullable=False, default="0.1")
    assigned_by = db.Column(
        db.Integer, db.ForeignKey('User.id'), nullable=False)
    fixed_case_date = db.relationship("FixedCaseDate", backref="Case")

    def __repr__(self):
        return self.id


# case schema
class CaseSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'assignedAdvocate', 'affidavit', 'chargeSheet',
                  'caseCreatedTime', 'lastModified', 'caseStatus', 'severityIndex', 'assignedBy')


# init schema
case_schema = CaseSchema()
cases_schema = CaseSchema(many=True)


class CaseController(Resource):
    def get(self):
        case = Case.query.all()
        return cases_schema.jsonify(case)

    def post(self):
        name = request.form.get('case_name')
        assignedAdvocate = request.form.get("assigned_advocate")
        affidavit = request.files['affidavit']
        chargesheet = request.files["charge_sheet"]
        assignedby = request.form.get("assigned_by")
        affidavit_rename = "{}_{}_affidavit.pdf".format(name, secrets.token_hex(10))
        affidavit.save(os.path.join(app.config["UPLOAD_FOLDER"] + "/affidavit/", secure_filename(affidavit_rename)))
        chargesheet_rename = "{}_{}_chargesheet.pdf".format(name, secrets.token_hex(10))
        chargesheet.save(
            os.path.join(app.config["UPLOAD_FOLDER"] + "/chargesheet/", secure_filename(chargesheet_rename)))

        case = Case(name=name, assignedAdvocate=assignedAdvocate, affidavit=affidavit_rename,
                    chargeSheet=chargesheet_rename, assignedBy=assignedby)
        print(name, assignedAdvocate, affidavit, chargesheet, assignedby)
        data = dict(request.form)
        print(data)
        db.session.add(case)
        db.session.commit()
        return successAsJson()


class GenericCaseController(Resource):
    def get(self, caseno):
        case = Case.query.filter_by(id=caseno).all()
        return cases_schema.jsonify(case)

    def delete(self, caseno):
        case = Case.query.filter_by(id=caseno).all()
        db.seesion.delete(case)
        db.session.commit()

    def put(self, caseno):
        case = Case.query.filter_by(id=caseno).all()
        case.name = request.form.get('name')
        case.assignedAdvocate = request.form.get('assignedAdvocate')
        case.affidivit = request.form.get('affidivi')
        case.chargesheet = request.form.get('chargesheet')
        case.casestatus = request.form.get('casestatus')
        case.sevirity = request.form.get('sevirity')
        case.assignedby = request.form.get('assignedby')
        case.fixedCaseDates = request.form.get('fixedCaseDates')
        db.session.commit()


class FixedCaseDate(db.Model):
    __tablename__ = 'fixed_case_date'
    id = db.Column(db.Integer, primary_key=True)
    case = db.Column(db.Integer, db.ForeignKey("Case.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    courthouse = db.Column(db.Integer, db.ForeignKey("Courthouse.id"), nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.id


class FixedCaseSchema(ma.Schema):
    class Meta:
        fields = ('id', 'case', 'date', 'createdby', 'type')


# init schema
fixed_case_schema = FixedCaseSchema()
fixed_cases_schema = FixedCaseSchema(many=True)


class FixedDateController(Resource):
    def get(self, fix_id):
        fixed_case_date = FixedCaseDate.filter_by(id=fix_id).all()
        return fixed_case_schema.jsonify(fixed_case_date)

    def put(self, fix_id):
        fixed_case_date = FixedCaseDate.filter_by(id=fix_id).all()
        fixed_case_date.case = request.form.get('case')
        fixed_case_date.date = request.form.get('date')
        fixed_case_date.createdBy = request.form.get('createdBy')
        fixed_case_date.type = request.form.get('type')
        db.session.commit()

    def delete(self, fix_id):
        fixed_case_date = FixedCaseDate.filter_by(id=fix_id).all()
        db.seesion.delete(fixed_case_date)
        db.session.commit()


class GenericFixedDateController(Resource):
    def get(self):
        fixed_case_date = FixedCaseDate.query.all()
        return fixed_cases_schema.jsonify(fixed_case_date)

    def post(self):
        case = request.json['case']
        date = request.json['date']
        createdBy = request.json['createdBy']
        type = request.json['type']
        fixed_date = FixedCaseDate(
            case=case, date=date, createdBy=createdBy, type=type)
        db.session.add(fixed_date)
        db.session.commit()


class JudgeCasePreference(db.Model):
    __tablename__ = 'judge_case_preference'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    section = db.Column(db.String, nullable=False)
    preferenceOrder = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self.user + self.preferenceOrder


class JudgeCasePreferenceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user', 'section', 'preferenceoder')


# init schema
judge_case_preference_schema = JudgeCasePreferenceSchema()
judge_case_preferences_schema = JudgeCasePreferenceSchema(many=True)


class ScheduleController(Resource):
    def get(self):
        cases = Case.query.order_by(Case.caseCreatedTime).limit(10)
        return cases_schema.jsonify(cases)


class LoginController(Resource):
    def post(self):
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            print(username, password)
            user = User.query.filter(User.username == username and User.password == password).one()
            if user != None:
                return user_schema.jsonify(user)
            return jsonify({
                "status": "Authentication failed"
            })
        except Exception as e:
            traceback.print_exc()
            return exceptionAsAJson("login post", str(e))


api.add_resource(CourthouseController, '/courthouse')
api.add_resource(UserController, '/user')
api.add_resource(GenericUserController, '/user/<int:userno>')
api.add_resource(CaseController, '/case')
api.add_resource(GenericCaseController, '/case/<int:caseno>')
api.add_resource(RequestController, '/request')
api.add_resource(GenericRequestController, '/request/<int:reqid>')
api.add_resource(GenericFixedDateController, '/fixedcasedate')
api.add_resource(FixedDateController, '/fixedcasedate/<int:fixid>')
api.add_resource(LoginController, "/login")
api.add_resource(ScheduleController, "/schedule")

# run Server
if __name__ == '__main__':
    app.run(debug=True)
