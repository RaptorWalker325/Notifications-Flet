import flet as ft
import flet_datatable2 as ftd
from Lib import json
import uuid
from datetime import datetime
from pathlib import Path
import os

class Notification: 
    def __init__(self,  id:str ,name: str, date: str):
        self.id = id
        self.name = name
        self.date = date
notifications = []

class Settings:
    def __init__(self,  name:str ,value: str):
        self.name = name
        self.value = value
settings = []

def gen_uuid():
    return str(uuid.uuid4())

def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"   # fallback for local runs
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()
assets_dir = get_assets_dir()

def add_notification(id, name, date):
    notification = Notification(id, name, date)
    notifications.append(notification)

def edit_notification(id, name, date):
    notifications[id].name = name
    notifications[id].date = date

def search_notification(id):
    index = 0
    sid = id
    for notification in notifications:
        uid = notification.id
        if uid == sid:
            return index
        index = index+1
    
def delete_notification(index):
    del notifications[index]

def open_data():
    try: 
        with open(assets_dir/'data.json', 'r') as file:
            data = json.load(file)
        for item in data:
            add_notification(item['id'],item['name'], item['date'])
    except:
        print("No existing data found.")

def saving_data():
    with open(assets_dir/'data.json', 'w') as file:
        newdata = []
        for notification in notifications:
            newdata.append({"id":notification.id, "name": notification.name, "date": notification.date})
        file.write(json.dumps(newdata, indent=4))  

def load_settings():
    def load(name, value):
        setting = Settings(name,value)
        settings.append(setting)
    try: 
        with open(assets_dir/'settings.json', 'r') as file:
            data = json.load(file)
        for item in data:    
            load(item['name'], item['value'])
    except Exception as e:
        print(e)

def main(page = ft.Page):
    page.appbar = ft.AppBar(
        title=ft.Text("Notifications App"),
        bgcolor='grey')
    page.padding=0
    
    error = ft.Text(color='red')
    def reset_error(): error.value = ''
    
    def add_edit(id,d_name,d_date,position,data):
        if id == '': title = ft.Text('Adding a new notification')
        else: title = ft.Text('Editing a notification')
        name = ft.TextField(value=(f"{d_name}"),label="Name", hint_text="Do laundry")
        date = ft.TextField(value=d_date,label="Date", hint_text="12/06/2026",suffix=
        ft.Button(
                "Pick date",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda _: page.show_dialog(ft.DatePicker(
                    value=datetime.today(),
                    entry_mode= ft.DatePickerEntryMode.CALENDAR_ONLY,
                    on_change=lambda e: handle_date(e)
                    )),
                ))
        def handle_date(e):
            get_date = datetime.strftime(e.data,"%d/%m/%Y")
            date.value = get_date
        
        add_dialog = ft.AlertDialog(
        modal=True,
        title=title,
        content=ft.Row(controls=[name,date]),       
        actions=[
            error,
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.TextButton("Save", on_click=lambda e: handle_input(id,name.value,date.value,position,data)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss= reset_error
        )
        page.show_dialog(add_dialog)
        
    def add_table_notification(name,date):
        index = gen_uuid()
        add_notification(index,name,date)
        add_row(index,name,date,'')
        view_listing.update()
        saving_data()
        page.pop_dialog()
    
    def edit_table_notification(id,name,date,position,data):
        edit_notification(position, name, date)
        view_listing.rows.remove(data)
        view_listing.update()
        add_row(id,name,date,position)
        view_listing.update()
        saving_data()
        page.pop_dialog()
        
    def adding():
        add_edit('','','','','')
    
    def handle_input(id,name,date,position,data):
        if name != '':
            try:
                c_date = datetime.strptime(date,"%d/%m/%Y")
                n_date = datetime.strftime(c_date,"%d/%m/%Y")
                if id == '':
                    add_table_notification(name,n_date)
                else:
                    edit_table_notification(id,name,n_date,position,data)
            except:
                error.value = 'invalid date'
        else:
            error.value = 'fill all blank fields'
     
    def load_list():
        for notification in notifications:
            add_row(notification.id,notification.name,notification.date,'')
    def reload_list():
        view_listing.update()
    
    def settings_config():
        async def test_hours():
            try:
                datetime.time(datetime.strptime(hours.value,'%H:%M'))
                hours.error = None
                print("valid time")
                save.disabled = False
            except Exception as ex:
                await hours.focus()
                hours.error = 'Invalid Format(HH:MM)'
                save.disabled = True
                print(ex)
  
        today = ft.Checkbox(value=settings[0].value,label=settings[0].name)
        one_day = ft.Checkbox(value=settings[1].value,label=settings[1].name)
        seven_days = ft.Checkbox(value=settings[2].value,label=settings[2].name)
        fifteen_days = ft.Checkbox(value=settings[3].value,label=settings[3].name)
        thirty_days = ft.Checkbox(value=settings[4].value,label=settings[4].name)
        hours = ft.TextField(width=200,value=settings[5].value,label="Hours", hint_text="14:00",on_blur=test_hours)
        windows = ft.Checkbox(value=settings[6].value,label=settings[6].name)
        mail = ft.Checkbox(value=settings[7].value,label=settings[7].name,disabled=True)
        app = ft.Checkbox(value=settings[8].value,label=settings[8].name)
        email = ft.TextField(value=settings[9].value,label=settings[9].name,on_tap_outside=None,read_only=True)
        title = ft.TextField(value=settings[10].value,label=settings[10].name)
        body = ft.TextField(min_lines=3,max_lines=5,width=610,multiline=True,value=settings[11].value,label=settings[11].name)
        save = ft.TextButton("Save", on_click=lambda e: save_config())
        def save_config():
            page.pop_dialog()
            settings[0].value = today.value
            settings[1].value = one_day.value
            settings[2].value = seven_days.value
            settings[3].value = fifteen_days.value
            settings[4].value = thirty_days.value
            settings[5].value = hours.value
            settings[6].value = windows.value
            settings[7].value = mail.value
            settings[8].value = app.value
            settings[9].value = email.value
            settings[10].value = title.value
            settings[11].value = body.value
            with open(assets_dir/'settings.json', 'w') as file:
                newdata = []
                for setting in settings:
                    newdata.append({"name": setting.name, "value": setting.value})
                file.write(json.dumps(newdata, indent=4))  
            
        alert_settings = ft.AlertDialog(
        modal=True,
        title=ft.Text("Settings",align=ft.Alignment.CENTER),
        content=ft.Column(spacing=0,margin=0,controls=[
                ft.Container(
                    margin=10,
                    padding=10,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(controls=[
                    ft.Row(ft.Text("Notify in:")),
                    ft.Row(controls=[today,one_day,seven_days,fifteen_days,thirty_days])
                    ])),
                ft.Row(controls=[
                ft.Container(
                    margin=10,
                    padding=10,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(controls=[
                    ft.Row(ft.Text("Time to Notify:")),
                    ft.Row(controls=[hours])
                    ])),
                ft.Container(
                    width=400,
                    height=100,
                    margin=10,
                    padding=10,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(controls=[
                    ft.Text("Notify on:"),
                    ft.Row(controls=[windows,mail,app])
                    ]))]),
                ft.Container(
                    margin=10,
                    padding=10,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(controls=[
                    ft.Row(ft.Text("Email:")),
                    ft.Row(controls=[email,title]),
                    body
                    ])),
                ]
            ),
        actions=[save]
        )
        page.show_dialog(alert_settings)
    
    sidebar = ft.Container(
        width=180,
        expand_loose=True,
        padding=10,
        content=ft.Column(
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand_loose=True,
            controls=[
                ft.Column(
                    spacing = 20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand_loose=True,
                    controls=[
                    ft.Row(ft.Button(icon=ft.Icon(ft.Icons.LIST),content="LIST",expand=True,on_click=reload_list)),
                    ft.Row(ft.Button(icon=ft.Icon(ft.Icons.ADD),content="ADD",expand=True,on_click=adding)),
                    ft.Divider(height=3,thickness=3)]),
                ft.Row(ft.Button(icon=ft.Icon(ft.Icons.SETTINGS),content=ft.Text('SETTINGS'),expand=True,on_click=settings_config))
            ]
        ),
    )
    
    def deleting(e: ft.Event[ft.Button]) -> None:
        index = search_notification(e.control.key)
        data = e.control.data
        u_sure = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Are you sure?"),
        actions=[
            ft.TextButton("No", on_click=lambda e: page.pop_dialog()),
            ft.TextButton("Yes", on_click=lambda e: handle_delete(index,data)),
        ],
        actions_alignment=ft.MainAxisAlignment.END)
        page.show_dialog(u_sure)
        
    def handle_delete(index,data):
        delete_notification(index)
        view_listing.rows.remove(data)
        view_listing.update()
        saving_data()
        page.pop_dialog()
            
    def editing(e: ft.Event[ft.Button]) -> None:
        idrow = e.control.key
        data = e.control.data
        search = search_notification(idrow)
        add_edit(idrow,notifications[search].name,notifications[search].date,search,data)

    view_listing = ftd.DataTable2(
        expand=True,
        empty=ft.Text("This table is empty."),
        rows=[],
        columns=[
            ftd.DataColumn2(label=ft.Text("Name"),key='name'),
            ftd.DataColumn2(label=ft.Text("Date"),key='date'),
            ftd.DataColumn2(label=ft.Text("Edit"),key='edit'),
            ftd.DataColumn2(label=ft.Text("Delete"),key='delete'),
        ],
    )

    def add_row(index, name, date, position):
        row = ftd.DataRow2(
            specific_row_height=50,
            key=index,
            cells=[
                ft.DataCell(content=ft.Text(name)),
                ft.DataCell(content=ft.Text(date)),
                ft.DataCell(content=ft.Button('Edit',key=index,on_click=editing)),
                ft.DataCell(content=ft.Button('Delete',key=index,on_click=deleting)),
            ])
        row.cells[2].content.data = row
        row.cells[3].content.data = row
        
        if position == '':
            view_listing.rows.append(row)
        else:
            view_listing.rows.insert(position,row)
         
    load_list()
    page.add(
        ft.SafeArea(
            expand=True,
            expand_loose=True,
            minimum_padding= 0,
            content=ft.Row(
                margin=0,
                spacing=0,
                expand_loose=True,
                controls=[
                    sidebar,
                    ft.VerticalDivider(
                        width=5,
                        thickness=5,
                    ),
                    view_listing
                ],
            ),
        )
    )

open_data()
load_settings()
ft.run(main)
saving_data()