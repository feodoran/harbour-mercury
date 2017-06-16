/*
    Copyright (C) 2017 Christian Stemmle

    This file is part of Mercury.

    Mercury is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Mercury is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Mercury. If not, see <http://www.gnu.org/licenses/>.
*/

import QtQuick 2.0
import Sailfish.Silica 1.0


Page {
    id: page

    allowedOrientations: Orientation.All

    SilicaFlickable {
        anchors.fill: parent
        contentHeight: column.height

        Column {
            id: column

            width: parent.width
            spacing: Theme.paddingLarge

            PageHeader {
                id: header
                title: currentDialog.title
            }

            SilicaListView {

                id: messagesList
                height: page.height - header.height - (2*Theme.paddingLarge)
                width: parent.width
                anchors.left: parent.left
                anchors.right: parent.right

                VerticalScrollDecorator { flickable: messagesList }

                model: dialogModel

                delegate: ListItem {
                    id: delegate

                    contentHeight: dialog.height + Theme.paddingMedium
                    contentWidth: parent.width

                    Column {
                        id: dialog
                        width: parent.width - 2*Theme.paddingLarge
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: Theme.paddingMedium
                        x: Theme.paddingLarge

                        Text {
                            width: parent.width
                            color: delegate.highlighted ? Theme.highlightColor : Theme.primaryColor
                            text: model.name
                            font.bold: true
                        }
                        Text {
                            width: parent.width
                            color: delegate.highlighted ? Theme.highlightColor : Theme.primaryColor
                            text: model.message
                            wrapMode: Text.Wrap
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        telegram.fcall('request_messages', [currentDialog.entityID])
    }
}
