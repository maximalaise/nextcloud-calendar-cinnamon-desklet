const Desklet = imports.ui.desklet;
const St = imports.gi.St;
const GLib = imports.gi.GLib;
const Util = imports.misc.util;

function MyDesklet(metadata, desklet_id) {
    this._init(metadata, desklet_id);
}

MyDesklet.prototype = {
    __proto__: Desklet.Desklet.prototype,

    _init: function(metadata, desklet_id) {
        Desklet.Desklet.prototype._init.call(this, metadata, desklet_id);

        let parent = this.actor.get_parent();
        if (parent) {
            parent.remove_style_class_name("desklet-with-borders");
            parent.set_style("background: transparent !important; border: none !important; box-shadow: none !important; border-radius: 0 !important;");
        }

        this.setupUI();
    },

    setupUI: function() {
        this.container = new St.BoxLayout({vertical: true, style_class: "calendar-container"});
        this.headerLabel = new St.Label({style_class: "calendar-header"});
        this.spacerLabel = new St.Label({text: " "});
        this.textLabel = new St.Label({style_class: "calendar-text"});
        this.container.add(this.headerLabel);
        this.container.add(this.spacerLabel);
        this.container.add(this.textLabel);

        this.setContent(this.container);
        this.updateLabel();
    },

    updateLabel: function() {
        let path = this.metadata.path + "/nextcloud_display.txt";
        let [success, content] = GLib.file_get_contents(path);
        if (success) {
            let text = content.toString().replace(/\r/g, "");
            let lines = text.split("\n");
            this.headerLabel.set_text(lines[0]);
            this.textLabel.set_text(lines.slice(1).join("\n"));
        }
        this.timeout = GLib.timeout_add_seconds(0, 900, () => this.updateLabel());
    },

    on_desklet_clicked: function(event) {
        Util.spawnCommandLine("gnome-calendar");
    }
}

function main(metadata, desklet_id) {
    return new MyDesklet(metadata, desklet_id);
}
