import flet as ft
import flet_datatable2 as ftd
from Lib import json
import uuid
from datetime import datetime

class Notification: 
    def __init__(self,id:str ,name: str, date: str):
        self.id = id
        self.name = name
        self.date = date
notifications = []

def gen_uuid():
    return str(uuid.uuid4())

def add_notification(id,name, date):
    notification = Notification(id,name, date)
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
    print('sucess')

def open_data():
    try: 
        with open('./src/assets/data.json', 'r') as file:
            data = json.load(file)
        for item in data:
            add_notification(item['id'],item['name'], item['date'])
        print(len(notifications))
    except FileNotFoundError:
        print("No existing data found.")

def saving_data():
    with open('./src/assets/data.json', 'w') as file:
        newdata = []
        for notification in notifications:
            newdata.append({"id":notification.id, "name": notification.name, "date": notification.date})
        file.write(json.dumps(newdata, indent=4))  

def main(page = ft.Page):
    page.appbar = ft.AppBar(
        title=ft.Text("Notifications App"),
        bgcolor='grey')
    page.padding=0
    
    def add_edit(id,d_name,d_date,position,data):
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
        title=ft.Text("Adding a new notification"),
        content=ft.Row(controls=[name,date]),       
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.TextButton("Save", on_click=lambda e: adding_editing(id, name.value, date.value, position, data)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(add_dialog)
        
    def add_table_notification(name, date):
        index = gen_uuid()
        add_notification(index,name,date)
        add_row(index,name,date,'')
        view_listing.update()
        page.pop_dialog()
    
    def edit_table_notification(id, name, date, position, data):
        edit_notification(position, name, date)
        view_listing.rows.remove(data)
        add_row(id,name,date,position)
        view_listing.update()
        page.pop_dialog()
        
    def adding():
        add_edit('','','','','')
    
    def adding_editing(id, name, date, position, data):
        if id == '':
            add_table_notification(name, date)
            print('adding')
        else:
            edit_table_notification(id,name,date,position,data)
            print('editing')
          
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
                    ft.Row(ft.Button(icon=ft.Icon(ft.Icons.LIST),content="LIST",expand=True)),
                    ft.Row(ft.Button(icon=ft.Icon(ft.Icons.ADD),content="ADD",expand=True,on_click=adding)),
                    ft.Divider(height=3,thickness=3)]),
                ft.Row(ft.Button(icon=ft.Icon(ft.Icons.SETTINGS),content=ft.Text('SETTINGS'),expand=True))
            ]
        ),
    )
    
    def deleting(e: ft.Event[ft.Button]) -> None:
        index = search_notification(e.control.key)
        delete_notification(index)
        view_listing.rows.remove(e.control.data)
        
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
         
    for notification in notifications:
        add_row(notification.id,notification.name,notification.date,'')
    
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
ft.run(main)
saving_data()