import gtk
import model, util

class EditMode:
    def __init__(self, parent):
        self.parent = parent
        
        util.link_widgets(self.parent.xml,
                          self,
                          ['card_list',
                           'edit_frame',
                           'edit_toolbar',
                           'mainmenu_cards',
                           ])

        self.parent.xml.signal_autoconnect({
                'on_card_list_row_activated' :
                    lambda v,p,c: self.edit_selected_card(),
                })

        self.init_card_list()

        self.init_actions()
        self.init_menu()
        self.init_toolbar()

    def init_actions(self):
        self.action_group = gtk.ActionGroup('edit_mode_action_group')

        actions = []
        actions.append(('add_action',
                        'add_card_action',
                        'Add',
                        'Add a card to the deck',
                        gtk.STOCK_ADD,
                        '<Control>a',
                        lambda x: self.add_card()))
        actions.append(('edit_action',
                        'edit_card_action',
                        'Edit',
                        'Edit a card',
                        gtk.STOCK_EDIT,
                        '<Control>e',
                        lambda x: self.edit_selected_card()))
        actions.append(('delete_action',
                        'delete_card_action',
                        'Delete',
                        'Delete a card',
                        gtk.STOCK_DELETE,
                        '<Control>d',
                        lambda x: self.delete_selected_card()))

        actions.append(('do_review_action',
                        'do_review_action',
                        'Review',
                        'Start a review session',
                        gtk.STOCK_EXECUTE,
                        '<Control>r',
                        lambda x: self.parent.enter_review_mode()))

        for action in actions:
            a = gtk.Action(action[1],
                           action[2],
                           action[3],
                           action[4])
            setattr(self, action[0], a)
            self.action_group.add_action_with_accel(a, action[5])
            a.set_accel_group(self.parent.accel_group)
            a.connect_accelerator()
            a.connect('activate', action[6])

    def init_menu(self):
        m = self.mainmenu_cards.get_submenu()
        m.append(self.add_action.create_menu_item())
        m.append(self.edit_action.create_menu_item())
        m.append(self.delete_action.create_menu_item())
        m.append(gtk.SeparatorMenuItem())
        m.append(self.do_review_action.create_menu_item())

    def init_toolbar(self):
        t = self.edit_toolbar
        t.insert(self.add_action.create_tool_item(), -1)
        t.insert(self.edit_action.create_tool_item(), -1)
        t.insert(self.delete_action.create_tool_item(), -1)
        t.insert(gtk.SeparatorToolItem(), -1)
        t.insert(self.do_review_action.create_tool_item(), -1)        

    def enter_mode(self):
        self.edit_frame.show()
        self.edit_toolbar.show()
        self.mainmenu_cards.show()

    def exit_mode(self):
        self.edit_frame.hide()
        self.edit_toolbar.hide()
        self.mainmenu_cards.hide()

    def init_card_list(self):
        col = gtk.TreeViewColumn('Front')
        cell = gtk.CellRendererText()
        cell.set_fixed_height_from_font(1)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', model.FRONT_CIDX)
        col.set_sort_column_id(model.FRONT_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Back')
        cell = gtk.CellRendererText()
        cell.set_fixed_height_from_font(1)
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', model.BACK_CIDX)
        col.set_sort_column_id(model.BACK_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Bin')
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', model.BIN_CIDX)
        col.set_sort_column_id(model.BIN_CIDX)
        self.card_list.append_column(col)

        col = gtk.TreeViewColumn('Type')
        cell = gtk.CellRendererText()
        #cell.set_property('fontstyle', 'italic')
        col.pack_start(cell, True)
        col.add_attribute(cell, 'text', model.TYPE_CIDX)
        col.set_sort_column_id(model.TYPE_CIDX)
        self.card_list.append_column(col)        

        self.card_list.set_model(model.new_model())
        self.connect_model()

    def connect_model(self):
        model = self.card_list.get_model()
        model.connect('row-changed',
                      lambda m,p,i: self.parent.save_file_mgr.flag_change())
        model.connect('row-deleted',
                      lambda m,p: self.parent.save_file_mgr.flag_change())
        model.connect('row-inserted',
                      lambda m,p,i: self.parent.save_file_mgr.flag_change())

    def add_card(self):
        xml = gtk.glade.XML(self.parent.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        bin_combo = xml.get_widget('bin_combo')
        type_combo = xml.get_widget('type_combo')
        front_text = xml.get_widget('front_text_view')
        back_text = xml.get_widget('back_text_view')

        for w in dlg, bin_combo, type_combo, front_text, back_text:
            assert w

        bin_combo.set_active(0)
        type_combo.set_active(0)

        response = dlg.run()

        bin = bin_combo.get_active()
        cardtype = model.cardtypes[type_combo.get_active()]
        front = util.get_text(front_text)
        back = util.get_text(back_text)
        dlg.destroy()

        if not response == gtk.RESPONSE_OK: return
        if front == "" and back == "": return

        mdl = self.card_list.get_model()
        iter = mdl.append([front,
                           back,
                           bin,
                           cardtype])
        self.card_list.set_cursor(mdl.get_path(iter))

    def edit_selected_card(self):
        sel = self.card_list.get_selection()
        mdl,iter = sel.get_selected()
        if not iter: return

        bin,cardtype,front,back = mdl.get(iter,
                                          model.BIN_CIDX,
                                          model.TYPE_CIDX,
                                          model.FRONT_CIDX,
                                          model.BACK_CIDX)

        xml = gtk.glade.XML(self.parent.gladefile, 'CardEditorDlg')
        dlg = xml.get_widget('CardEditorDlg')
        dlg.set_transient_for(self.parent.main_window)
        
        bincombo = xml.get_widget('bin_combo')
        bincombo.set_active(bin)

        cardtypecombo = xml.get_widget('type_combo')
	cardtypecombo.set_active(model.cardtypes.index(cardtype))

        front_text = xml.get_widget('front_text_view')
        front_text.get_buffer().set_text(front)

        back_text = xml.get_widget('back_text_view')
        back_text.get_buffer().set_text(back)

        response = dlg.run()
        bin = bincombo.get_active()
        cardtype = model.cardtypes[cardtypecombo.get_active()]
        front = util.get_text(front_text)
        back = util.get_text(back_text)
        dlg.destroy()

        if not response == gtk.RESPONSE_OK: return
        if front == "" and back == "": return

        mdl.set(iter,
                model.BIN_CIDX, bin,
                model.FRONT_CIDX, front,
                model.BACK_CIDX, back,
                model.TYPE_CIDX, cardtype)

    def delete_selected_card(self):
        sel = self.card_list.get_selection()
        model,iter = sel.get_selected()
        if not iter: return

        dlg = gtk.MessageDialog(self.parent.main_window,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                'Delete entry?')
        rslt = dlg.run()
        dlg.destroy()
        if rslt == gtk.RESPONSE_NO: return

        model.remove(iter)

    def sync_ui(self):
        num_cards = len(self.card_list.get_model())
        have_cards = num_cards > 0
        self.edit_action.set_sensitive(have_cards)
        self.delete_action.set_sensitive(have_cards)
        self.do_review_action.set_sensitive(have_cards)
