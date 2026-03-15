const Desklet = imports.ui.desklet;
const St = imports.gi.St;
const GLib = imports.gi.GLib;
const Util = imports.misc.util;
const Settings = imports.ui.settings;
const Clutter = imports.gi.Clutter;

function MyDesklet(metadata, desklet_id) {
    this._init(metadata, desklet_id);
}

MyDesklet.prototype = {
    __proto__: Desklet.Desklet.prototype,

    _init: function(metadata, desklet_id) {
        Desklet.Desklet.prototype._init.call(this, metadata, desklet_id);

        this.settings = new Settings.DeskletSettings(this, this.metadata.uuid, desklet_id);
        this.settings.bindProperty(Settings.BindingDirection.IN, "view", "view", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "font-color", "fontColor", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "header-color", "headerColor", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "font-size", "fontSize", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "background-opacity", "backgroundOpacity", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "show-timestamp", "showTimestamp", this.onSettingsChanged, null);
        this.settings.bindProperty(Settings.BindingDirection.IN, "border-radius", "borderRadius", this.onSettingsChanged, null);

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
        this.timestampLabel = new St.Label({
            style_class: "calendar-timestamp",
            x_align: Clutter.ActorAlign.END,
            x_expand: true
        });
        this.container.add(this.headerLabel);
        this.container.add(this.spacerLabel);
        this.container.add(this.textLabel);
        this.container.add(this.timestampLabel);

        this.setContent(this.container);
        this.onSettingsChanged();
        this.startRefreshCycle();
    },

    startRefreshCycle: function() {
        Util.spawnCommandLine("python3 " + this.metadata.path + "/nextcloudfetcher.py");

        GLib.timeout_add_seconds(0, 10, () => {
            this.updateLabel();
            return false;
        });

        this.timeout = GLib.timeout_add_seconds(0, 900, () => {
            this.startRefreshCycle();
            return false;
        });
    },

    onSettingsChanged: function() {
        this.container.set_style(
            "background-color: rgba(30, 39, 46, " + this.backgroundOpacity + "); " +
            "border-radius: " + this.borderRadius + "px; " +
            "padding: 20px; " +
            "min-width: 250px;"
        );

        this.textLabel.set_style("color: " + this.fontColor + "; font-size: " + this.fontSize + "pt;");
        this.headerLabel.set_style("color: " + this.headerColor + "; font-size: " + this.fontSize + "pt; font-weight: bold;");
        this.timestampLabel.visible = this.showTimestamp;

        let config = JSON.stringify({
            view: this.view,
            showTimestamp: this.showTimestamp
        });
        let path = this.metadata.path + "/config.json";
        GLib.file_set_contents(path, config);

        this.startRefreshCycle();
    },

    updateLabel: function() {
        let path = this.metadata.path + "/nextcloud_display.txt";
        let [success, content] = GLib.file_get_contents(path);
        if (success) {
            let text = content.toString().replace(/\r/g, "");
            let lines = text.split("\n");
            this.headerLabel.set_text(lines[0]);
            let lastLine = lines[lines.length - 1];
            if (lastLine.startsWith("##")) {
                this.timestampLabel.set_text(lastLine.replace("##", ""));
                this.textLabel.set_text(lines.slice(1, -1).join("\n"));
            } else {
                this.textLabel.set_text(lines.slice(1).join("\n"));
                this.timestampLabel.set_text("");
            }
        }
    },

    on_desklet_clicked: function(event) {
        Util.spawnCommandLine("gnome-calendar");
    }
}

function main(metadata, desklet_id) {
    return new MyDesklet(metadata, desklet_id);
}
