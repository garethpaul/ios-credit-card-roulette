//
//  CardRouletteTests.swift
//  CardRouletteTests
//
//  Created by Gareth Jones  on 5/30/15.
//  Copyright (c) 2015 gpj. All rights reserved.
//

import UIKit
import XCTest
@testable import CardRoulette

class CardRouletteTests: XCTestCase {

    func testParticipantNameNormalizationTrimsWhitespace() {
        XCTAssertEqual(ParticipantListItem.normalizedName("  Hemal\n")!, "Hemal", "Participant names should be trimmed before saving")
    }

    func testParticipantNameNormalizationRejectsBlankNames() {
        XCTAssertNil(ParticipantListItem.normalizedName("  \n\t  "), "Blank participant names should be ignored")
        XCTAssertNil(ParticipantListItem.normalizedName(nil), "Missing participant names should be ignored")
    }

    func testParticipantItemFromAddParticipantSource() {
        let controller = ViewController()
        let source = AddParticipantViewController()
        let item = ParticipantListItem(name: "Hemal")
        source.participantItem = item

        XCTAssertTrue(controller.participantItemFromSegueSource(source) === item, "Add participant unwinds should provide their saved participant")
    }

    func testParticipantItemFromWinnerSource() {
        let controller = ViewController()
        let source = WinnerViewController()
        let item = ParticipantListItem(name: "Gareth")
        source.participantItem = item

        XCTAssertTrue(controller.participantItemFromSegueSource(source) === item, "Winner unwinds should provide their saved participant")
    }

    func testParticipantItemFromUnknownSourceReturnsNil() {
        let controller = ViewController()

        XCTAssertNil(controller.participantItemFromSegueSource(UIViewController()), "Unrecognized unwind sources should be ignored")
    }

}
