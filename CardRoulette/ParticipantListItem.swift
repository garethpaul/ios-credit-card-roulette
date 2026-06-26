//
//  ParticipantListItem.swift
//  CardRoulette
//
//  Created by Gareth Jones  on 5/31/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import Foundation

class ParticipantListItem: NSObject {

    var itemName = ""
    var completed: Bool = false
    var creationDate = Date()

    init(name: String) {
        self.itemName = name
        super.init()
    }

    private class func isVisibleNameScalar(_ scalar: Unicode.Scalar) -> Bool {
        let generalCategory = scalar.properties.generalCategory
        return !CharacterSet.whitespacesAndNewlines.contains(scalar) &&
            generalCategory != .control && generalCategory != .format
    }

    class func normalizedName(_ name: String?) -> String? {
        guard let participantName = name else {
            return nil
        }

        let participantScalars = participantName.unicodeScalars
        guard let firstVisibleScalarIndex = participantScalars.firstIndex(where: { scalar in
                  return isVisibleNameScalar(scalar)
              }),
              let lastVisibleScalarIndex = participantScalars.lastIndex(where: { scalar in
                  return isVisibleNameScalar(scalar)
              }) else {
            return nil
        }

        return String(participantName[firstVisibleScalarIndex...lastVisibleScalarIndex])
    }
    
}
